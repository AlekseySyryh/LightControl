from datetime import datetime, timedelta
from flask import Flask, request
from threading import Lock

app = Flask(__name__)

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
    resp = '''<!DOCTYPE html>
<html lang="ru">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Управление светом</title>
    <style>
        :root {
            font-size: 14px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
        }

        body {
            padding: 0;
            margin: 0;
            height: 100vh;
        }

        .app {
            background-color: white;
            color: rgba(0, 0, 0, 0.8);
        }

        .app-header {
            font-weight: 400;
            font-size: 24px;
            padding: 8px 16px;
            margin: 0;
            text-transform: uppercase;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .app-main {
            padding: 8px 16px 32px 16px;
        }

        .info-text {
            font-size: 20px;
            margin-top: 8px;
        }

        .section-title {
            margin: 0;
            font-size: 16px;
            font-weight: 700;
            color: rgba(0, 0, 0, 0.7);
        }

        .ripple {
            background-position: center;
            transition: background 0.8s;
        }

        .ripple:hover {
            background: #47a7f5 radial-gradient(circle, transparent 1%, #47a7f5 1%) center/15000%;
        }

        .ripple:active {
            background-color: #6eb9f7;
            background-size: 100%;
            transition: background 0s;
        }

        .button {
            flex: 1 1 auto;
            margin-top: 8px;
            border: none;
            border-radius: 2px;
            padding: 12px 18px;
            font-size: 16px;
            text-transform: uppercase;
            cursor: pointer;
            color: white;
            background-color: #2196f3;
            box-shadow: 0 0 4px #999;
            outline: none;
        }

        .timer-form-section,
        .enable-light-buttons-section {
            margin-top: 32px;
        }

        .enable-light-buttons {
            display: flex;
            flex-flow: row wrap;
            justify-content: space-between;
        }



        .timer-form {
            display: grid;
            grid-template-columns: 32px 1fr;
            grid-column-gap: 8px;
            grid-template-areas: "l1 i1""l2 i2""b b";
        }

        .timer-label-start {
            grid-area: l1;
        }

        .timer-label-stop {
            grid-area: l2;
        }

        .timer-input-start {
            grid-area: i1;
        }

        .timer-input-stop {
            grid-area: i2;
        }

        .timer-apply-button {
            grid-area: b;
        }

        .timer-label {
            font-size: 20px;
            margin-top: 12px;
        }

        .timer-input {
            width: auto;
            margin-top: 8px;
            font-size: 20px;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
        }


        @media (min-width: 400px) {
            .enable-light-buttons .button {
                max-width: 45vw;
            }

            .timer-form {
                grid-template-columns: 32px 1fr calc(10vw - 48px) 32px 1fr;
                grid-template-areas: "l1 i1 . l2 i2""b b b b b";
            }
        }

        @media (min-width: 600px) {
            body {
                height: 100vh;
                overflow: auto;
                background: linear-gradient(#388E3C 120px, #C8E6C9 120px);
                background-attachment: fixed;
            }
            .app {
                width: 600px;
                margin-left: auto;
                margin-right: auto;
                border-radius: 2px;
                box-shadow: 0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23);
                transform: translateY(64px);
            }

            .app-header {
                font-size: 32px;
            }

            .enable-light-buttons .button {
                max-width: 264px;
            }

            .timer-form {
                grid-template-columns: 32px 220px 1fr 32px 220px;
                grid-template-areas: "l1 i1 . l2 i2""b b b b b";
            }
        }
    </style>
</head>

<body>
    <div class="app">
        <header>
            <h1 class="app-header">Управление светом</h1>
        </header>
        <main class="app-main">
            <section>'''

    time = datetime.utcnow() + timedelta(hours=5)

    resp += '<div class="info-text">Местное время: {:02d}:{:02d}:{:02d}</div>'.format(time.hour, time.minute,
                                                                                      time.second)
    if isOn():
        resp += '<div class="info-text">Свет включен.</div>'
    else:
        resp += '<div class="info-text">Свет выключен.</div>'
    if timeOn:
        resp += '<div class="info-text">Таймер с {:02d}:{:02d} по {:02d}:{:02d}</div>'.format(hstart, mstart, hstop,
                                                                                              mstop)
    else:
        resp += '<div class="info-text">Ручной режим.<div>'

    resp += '''
            <section class="enable-light-buttons-section">
                <h2 class="section-title">Ручное управление</h2>
                <div class="enable-light-buttons">
                         <button type="button" "location.href=\'on\'" class="ripple button">Включить свет</button>
                            <button type="button" "location.href=\'off\'" class="ripple button">Выключить свет</button>
                      </div>
            </section>
            
            <section class="timer-form-section">
                <h2 class="section-title">Настройка таймера</h2>
                <form class="timer-form" action="timer">
                    <label for="start" class="timer-label timer-label-start">C:</label>
                    <input type="time" id="start" name="start" class="timer-input timer-input-start" value="{:02d}:{:02d}" />
                    <label for="stop" class="timer-label timer-label-stop">По:</label>
                    <input type="time" id="stop" name="stop" class="timer-input  timer-input-stop" value="{:02d}:{:02d}" />
                    <button type="submit" class="timer-apply-button ripple button">Включить таймер</button>
                </form>
            </section>
        </main>
    </div>
</body>

</html>'''.format(hstart, mstart, hstop, mstop)
    return resp


@app.route("/")
def hello():
    if isOn():
        return "LON"
    else:
        return "LOFF"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
