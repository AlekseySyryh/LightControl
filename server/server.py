from datetime import datetime, timedelta
from flask import Flask, request, send_from_directory
from threading import Lock
import io

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
    global file

    time = datetime.utcnow() + timedelta(hours=5)

    if isOn():
        lstr = 'включен'
    else:
        lstr = 'выключен'
    if timeOn:
        tstr = 'Таймер с {:02d}:{:02d} по {:02d}:{:02d}'.format(hstart, mstart, hstop, mstop)
    else:
        tstr = "Ручной режим"

    resp = file.format(time.hour, time.minute, time.second, lstr, tstr, hstart, mstart, hstop, mstop)
    return resp


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
    file = f.read()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
