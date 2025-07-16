from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import random

app = Flask(__name__)
socketio = SocketIO(app)

rooms = {}
BOARD_SIZE = 30

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_room')
def create_room():
    sid = request.sid
    while True:
        room_id = str(random.randint(1000, 9999))
        if room_id not in rooms:
            break

    rooms[room_id] = {
        'players': [sid],
        'board': [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
        'turn': 'X'
    }
    join_room(room_id)
    emit('room_created', {'room_id': room_id})

@socketio.on('join_room')
def join_room_event(data):
    sid = request.sid
    room_id = data.get('room_id')

    if room_id not in rooms:
        emit('error', {'message': 'Room ID មិនមាន'})
        return

    room = rooms[room_id]
    if len(room['players']) >= 2:
        emit('error', {'message': 'បន្ទប់ពេញហើយ'})
        return

    room['players'].append(sid)
    join_room(room_id)

    if len(room['players']) == 2:
        socketio.emit('game_started', {
            'room': room_id,
            'turn': room['turn'],
            'players': room['players']
        }, room=room_id)
    else:
        emit('waiting_for_player', {'message': 'រង់ចាំអ្នកលេងទី 2 ចូលបន្ទប់'})

@socketio.on('make_move')
def make_move(data):
    sid = request.sid
    room_id = data.get('room')
    x, y = data.get('x'), data.get('y')

    if room_id not in rooms:
        emit('error', {'message': 'Room មិនមាន'})
        return

    room = rooms[room_id]
    if sid not in room['players']:
        emit('error', {'message': 'អ្នកមិននៅក្នុងបន្ទប់នេះ'})
        return

    player_index = room['players'].index(sid)
    symbol = 'X' if player_index == 0 else 'O'

    if room['turn'] != symbol:
        return  # មិន alert / error ត្រូវ logic UI

    if room['board'][x][y] != '':
        return  # cell មានរួច

    room['board'][x][y] = symbol
    room['turn'] = 'O' if symbol == 'X' else 'X'

    socketio.emit('move_made', {'x': x, 'y': y, 'symbol': symbol}, room=room_id)

    if check_winner(room['board'], x, y, symbol):
        socketio.emit('game_over', {'winner': symbol}, room=room_id)
        # Reset board for next game automatically
        room['board'] = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        room['turn'] = 'X'

def check_winner(board, x, y, symbol):
    directions = [(1,0),(0,1),(1,1),(1,-1)]
    for dx, dy in directions:
        count = 1
        for dir in [1,-1]:
            i = 1
            while True:
                nx = x + i*dx*dir
                ny = y + i*dy*dir
                if 0 <= nx < len(board) and 0 <= ny < len(board[0]) and board[nx][ny] == symbol:
                    count += 1
                    i += 1
                else:
                    break
        if count >= 5:
            return True
    return False

if __name__ == '__main__':
    socketio.run(app, debug=True)
