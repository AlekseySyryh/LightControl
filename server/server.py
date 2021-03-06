from datetime import datetime, timedelta
from flask import Flask, request, send_from_directory, send_file
from threading import Lock
import io
import psycopg2
import pandas as pd
import tempfile

app = Flask(__name__, static_url_path='')

lightOn = True
timeOn = True
hstart = 9
hstop = 18
mstart = 0
mstop = 0
lock = Lock()

@app.route("/on")
def on():
    global lightOn
    global timeOn
    global lock
    lock.acquire()
    try:
        with open('log.txt', 'a') as f:
            f.write('{} {} SET MODE ON\n'.format(datetime.now(), request.remote_addr))
    finally:
        lock.release()
    lightOn = True
    timeOn = False
    return '<head><meta http-equiv="refresh" content="0;URL=status" /></head>'


@app.route("/off")
def off():
    global lightOn
    global timeOn
    global lock
    lock.acquire()
    try:
        with open('log.txt', 'a') as f:
            f.write('{} {} SET MODE OFF\n'.format(datetime.now(), request.remote_addr))
    finally:
        lock.release()
    timeOn = False
    lightOn = False
    return '<head><meta http-equiv="refresh" content="0;URL=status" /></head>'


def isOn():
    global lightOn
    global timeOn
    global hstart
    global hstop
    global mstart
    global mstop
    if timeOn:
        now = datetime.utcnow() + timedelta(hours=5)
        begin = datetime.combine(now.date(), datetime.min.time()) + timedelta(hours=hstart, minutes=mstart)
        end = datetime.combine(now.date(), datetime.min.time()) + timedelta(hours=hstop, minutes=mstop)
        if begin < end:
            return now > begin and now < end
        else:
            return (now > (begin + timedelta(days=-1)) and now < end) or (
                    now > begin and now < (end + timedelta(days=1)))
    else:
        return lightOn


@app.route("/timer")
def timer():
    global lightOn
    lightOn = False
    global timeOn
    timeOn = True
    global hstart
    global hstop
    global mstart
    global mstop
    global lock
    start = request.args.get('start')
    stop = request.args.get('stop')
    lock.acquire()
    try:
        with open('log.txt', 'a') as f:
            f.write('{} {} SET MODE TIME ({}-{})\n'.format(datetime.now(), request.remote_addr, start, stop))
    finally:
        lock.release()
    hstart, mstart = [int(x) for x in start.split(':')]
    hstop, mstop = [int(x) for x in stop.split(':')]
    return '<head><meta http-equiv="refresh" content="0;URL=status" /></head>'


@app.route("/status")
def status():
    global lightOn
    global timeOn
    global hstart
    global hstop
    global mstart
    global mstop
    global filecont

    time = datetime.utcnow() + timedelta(hours=5)

    if isOn():
        lstr = 'включен'
    else:
        lstr = 'выключен'
    if timeOn:
        tstr = 'Таймер с {:02d}:{:02d} по {:02d}:{:02d}'.format(hstart, mstart, hstop, mstop)
    else:
        tstr = "Ручной режим"

    resp = filecont.format(time.hour, time.minute, time.second, lstr, tstr, hstart, mstart, hstop, mstop)
    return resp


@app.route('/scudxlsx')
def scudxlsx():
    tf = tempfile.NamedTemporaryFile()
    month = request.args.get('month')
    conn = psycopg2.connect(dbname='ender', host='localhost')
    cursor = conn.cursor()
    cursor.execute(""
                   "select distinct "
                   "    name "
                   "from "
                   "    scud "
                   "inner join "
                   "    scud_user "
                   "on "
                   "    scud.id=scud_user.id "
                   "where "
                   "    date_trunc('month',ts+'5 hour') = date('{}-01');".format(month))
    rows = cursor.fetchall()
    names = []
    for row in rows:
        names.append(row[0])

    cursor.execute("select distinct "
                   "    date_trunc('day',ts+'5 hour')::date date "
                   "from "
                   "    scud "
                   "where "
                   "    date_trunc('month',ts+'5 hour') = date('{}-01')".format(month))
    rows = cursor.fetchall()
    cols = []
    for row in rows:
        cols.append(row[0])
    df = pd.DataFrame(columns=cols, index=names)

    cursor.execute("select "
                   "    name,"
                   "    date_trunc('day',ts+'5 hour')::date date,"
                   "    date_trunc('second',min(ts+'5 hour'))::time ints,"
                   "    date_trunc('second',max(ts+'5 hour'))::time outts "
                   "from "
                   "    scud "
                   "inner join "
                   "    scud_user "
                   "on "
                   "    scud.id=scud_user.id "
                   "where "
                   "    date_trunc('month',ts+'5 hour') = date('{}-01') "
                   "group by "
                   "    name,"
                   "    date_trunc('day',ts+'5 hour')"
                   "order by "
                   "    date_trunc('day',ts+'5 hour'),name;".format(month))
    rows = cursor.fetchall()
    for row in rows:
         df.loc[row[0],row[1]] = "{} - {}".format(row[2],row[3])

    writer = pd.ExcelWriter(tf.name, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    cf = writer.book.add_format({'align':'center'});
    worksheet = writer.sheets['Sheet1']
    worksheet.set_column(0,0,40,cf)
    worksheet.set_column(1,32,20,cf)
    writer.save()
    buffer = io.BytesIO()
    with open(tf.name, 'rb') as f:
        buffer.write(f.read(-1))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, attachment_filename='report.xlsx', cache_timeout=-1)

@app.route("/scudreport")
def scudreport():
    global filescud
    time = datetime.utcnow() + timedelta(hours=5)
    month = request.args.get('month')

    if month is None:
        report = ""
    else:
        conn = psycopg2.connect(dbname='ender', host='localhost')
        cursor = conn.cursor()
        cursor.execute(""
                       "select "
                       "    name,"
                       "    date_trunc('day',ts+'5 hour')::date date,"
                       "    date_trunc('second',min(ts+'5 hour'))::time ints,"
                       "    date_trunc('second',max(ts+'5 hour'))::time outts "
                       "from "
                       "    scud "
                       "inner join "
                       "    scud_user "
                       "on "
                       "    scud.id=scud_user.id "
                       "where "
                       "    date_trunc('month',ts+'5 hour') = date('{}-01') "
                       "group by "
                       "    name,"
                       "    date_trunc('day',ts+'5 hour')"
                       "order by "
                       "    date_trunc('day',ts+'5 hour'),name;".format(month))
        rows = cursor.fetchall()
        report = '<table border class="report-table"><tr><th>ФИО</th><th>День</th><th>Вход</th><th>Выход</th></tr>'
        for row in rows:
            report += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</th></tr>".format(row[0], row[1], row[2], row[3])
        report += "</table>" \
                  '<a href="scudxlsx?month={:s}" class="report-xls-url ripple button">XLSX</a>'.format(month)
        conn.commit()
        conn.close()
    return filescud.format(time.year, time.month, report)

@app.route("/meas")
def meas():
    conn = psycopg2.connect(dbname='ender', host='localhost')
    cursor = conn.cursor()
    aq = int(request.args.get('aq'))
    t = request.args.get('t')
    p = 0.75 * float(request.args.get('p')) / 100
    h = request.args.get('h')
    time = datetime.utcnow()
    cursor.execute("insert into data (ts,co,t,p,h) values ('{}',{},{},{},{});".format(time, aq, t, p, h))
    conn.commit()
    conn.close()
    return "DONE"

@app.route("/scud")
def scud():
	conn = psycopg2.connect(dbname='ender',host='localhost')
	cursor = conn.cursor()
	id = int(request.args.get('id'))
	print(id)
	time = datetime.utcnow()
	cursor.execute("insert into scud (ts,id) values ('{}',{});".format(time,id))
	conn.commit()
	cursor.execute("SELECT getMelody({})".format(id));
	rows = cursor.fetchall()
	conn.close()
	if len(rows) > 0:
		return rows[0][0]
	else:
		return "440,100"

@app.route("/style.css")
def style():
    return send_from_directory('', 'style.css')


@app.route("/favicon.ico")
def favicon():
    return send_from_directory('', 'favicon.ico')

@app.route("/")
def hello():
    if isOn():
        return "LON"
    else:
        return "LOFF"


with io.open('control.html', mode='rt', encoding='utf-8') as f:
    filecont = f.read()

with io.open('scudreport.html', mode='rt', encoding='utf-8') as f:
    filescud = f.read()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
