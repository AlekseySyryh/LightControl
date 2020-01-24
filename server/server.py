from datetime import datetime, timedelta
from flask import Flask, request, send_from_directory
from threading import Lock
import io
import psycopg2

app = Flask(__name__, static_url_path='')

lightOn = True
timeOn = False
hstart = 0
hstop = 0
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
        report = "<dt><tr><th>Name</th><th>Date</th><th>In</th><th>Out</th></tr>"
        for row in rows:
             report += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</th></tr>".format(row[0], row[1], row[2], row[3])
        report += "</dt>"
        print(report)
        conn.commit()
        conn.close()
    return filescud.format(time.year, time.month, report)

@app.route("/meas")
def meas():
	conn = psycopg2.connect(dbname='ender',host='localhost')
	cursor = conn.cursor()
	aq = int(request.args.get('aq'))
	t = request.args.get('t')
	p = 0.750061677078540615715689846343*float(request.args.get('p'))/100
	h = request.args.get('h')
	time = datetime.utcnow()
	cursor.execute("insert into data (ts,co,t,p,h) values ('{}',{},{},{},{});".format(time,aq,t,p,h))
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
	conn.close()
	return "DONE"

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
