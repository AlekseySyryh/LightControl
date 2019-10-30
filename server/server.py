from datetime import datetime, timedelta
from flask import Flask,request

app = Flask(__name__)

lightOn = True
timeOn = False
hstart = 0
hstop = 0
mstart = 0
mstop = 0

@app.route("/on")
def on():
	global lightOn
	global timerOn
	lightOn = True
	timerOn = False
	return status()


@app.route("/off")
def off():
	global lightOn
	global timerOn
	timerOn = False
	lightOn = False
	return status()

def isOn():
	global lightOn
	global timeOn
	global hstart
	global hstop
	global mstart
	global mstop
	if timeOn:
		now = datetime.utcnow() + timedelta(hours=5)
		begin = datetime.combine(now.date(), datetime.min.time()) + timedelta(hours=hstart,minutes=mstart)
		end = datetime.combine(now.date(), datetime.min.time()) + timedelta(hours=hstop, minutes=mstop)
		if begin < end:
			return now > begin and now < end
		else:
			return (now > (begin + timedelta(days=-1)) and now < end) or (now > begin and now < (end + timedelta(days=1)))
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
	start = request.args.get('start')
	stop = request.args.get('stop')
	hstart, mstart = [int(x) for x in start.split(':')]
	hstop, mstop = [int(x) for x in stop.split(':')]
	return '<head><meta http-equiv="refresh" content="1;URL=status" /></head>'

@app.route("/status")
def status():
	global lightOn
	global timeOn
	global hstart
	global hstop
	global mstart
	global mstop
	resp = '<!DOCTYPE html>' \
		   '<html lang="ru">' \
		   '	<head>' \
		   '	<meta charset="UTF-8">' \
		   '	<title>Light Control</title>' \
		   '</head>' \
		   '<body>'
	time = datetime.utcnow() + timedelta(hours=5)

	resp += 'Местное время: {:02d}:{:02d}:{:02d}<br>'.format(time.hour,time.minute,time.second)
	if isOn():
		resp += 'Свет включен.<br>'
	else:
		resp += 'Свет выключен.<br>'
	if timeOn:
		resp += 'Таймер с {:02d}:{:02d} по {:02d}:{:02d}<br>'.format(hstart,mstart,hstop,mstop)
	else:
		resp += 'Ручной режим.<br>'

	resp += '<br>' \
			'<button onclick="location.href=\'on\'" style="height:20px;width:100px" type="button">Вкл</button><br>' \
			'<button onclick="location.href=\'off\'" style="height:20px;width:100px" type="button">Выкл</button><br><br>' \
			'<form action="timer">' \
			'<table>' \
			'<tr><td>С:</td><td><input type="time" name="start"/></td></tr>' \
			'<tr><td>По:</td><td><input type="time" name="stop"/></td></tr>' \
			'</table>' \
			'<input type="submit" style="height:20px;width:100px" value="Таймер"/></form></body></html>'
	return resp


@app.route("/")
def hello():
	if isOn():
		return "LON"
	else:
		return "LOFF"


if __name__ == "__main__":
	app.run(host='0.0.0.0', port=8080)
