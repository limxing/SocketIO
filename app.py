from flask import Flask,render_template,session,request
from flask_socketio import SocketIO,emit,join_room,leave_room,close_room,rooms,disconnect
from threading import Lock
import tushareData

async_mode = None

app=Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

def background_thread():
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',{'data':'Server generated ecent','count':count})


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event')
def test_message(message):
    print(message)
    session['receive_count'] = session.get('receive_count', 0)+1
    emit('my_response', {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_ping')
def ping_pong():
    emit('my_pong')


@socketio.on('connect')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)
    emit('my_response',{'data':'Connected','count':0})


@socketio.on('disconnect_request')
def disconnect_request():
    session['receive_count'] = session.get('receive_count',0)+1
    emit('my_response',{'data':'Disconnected','count':session['receive_count']})
    disconnect()


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)


@socketio.on('get_company_notices')
def test_company_notices(message):
    id = message['data']
    data = tushareData.getNotices(id)
    emit('my_response', {'data': data.to_json(orient='index'), 'count': 0})
    # return

if __name__ == '__main__':
    socketio.run(app,debug=True)
