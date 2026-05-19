from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading")

rooms = {}  # 🔥 stores all rooms

def create_room(room):
    rooms[room] = {
        "board": [" " for _ in range(9)],
        "players": {},
        "turn": "X"
    }

def check_winner(b):
    wins = [(0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)]
    for x,y,z in wins:
        if b[x] == b[y] == b[z] and b[x] != " ":
            return b[x],(x,y,z)
    return None,None

@app.route("/")
def home():
    return render_template("index.html")

# 🔥 JOIN ROOM
@socketio.on("join_room")
def handle_join(data):
    room = data["room"]

    if room not in rooms:
        create_room(room)

    join_room(room)

    room_data = rooms[room]

    if len(room_data["players"]) < 2:
        player = "X" if "X" not in room_data["players"].values() else "O"
        room_data["players"][request.sid] = player
        emit("player_assign", {"player": player})
    else:
        emit("player_assign", {"player": "spectator"})

    emit("game_update", {
        "board": room_data["board"],
        "winner": None,
        "turn":room_data["turn"]
    }, to=room)

# 🔥 MOVE
@socketio.on("make_move")
def handle_move(data):
    room = data["room"]
    cell = data["cell"]

    room_data = rooms[room]
    player = room_data["players"].get(request.sid)

    # ❌ not your turn
    if player != room_data["turn"]:
        return

    # ❌ already filled
    if room_data["board"][cell] != " ":
        return

    # ✅ make move
    room_data["board"][cell] = player

    winner , combo= check_winner(room_data["board"])

    # ✅ WIN
    if winner:
        emit("game_update", {
            "board": room_data["board"],
            "winner": winner,
            "combo" : combo,
            "turn": room_data["turn"]
        }, to=room)

    # ✅ DRAW
    elif " " not in room_data["board"]:
        emit("game_update", {
            "board": room_data["board"],
            "winner": "Draw",
            "turn": room_data["turn"]
        }, to=room)

    # ✅ CONTINUE
    else:
        room_data["turn"] = "O" if player == "X" else "X"

        emit("game_update", {
            "board": room_data["board"],
            "winner": None,
            "turn": room_data["turn"]
        }, to=room)



    @socketio.on("play_again")
    def handle_play_again(data):
        room = data["room"]

        rooms[room]["board"] = [" " for _ in range(9)]
        rooms[room]["turn"] = "X"

        emit("game_update", {"board": rooms[room]["board"],"winner": None,"turn": "X"}, to=room)

# 🔥 DISCONNECT
@socketio.on("disconnect")
def handle_disconnect():
    for room in rooms:
        if request.sid in rooms[room]["players"]:
            del rooms[room]["players"][request.sid]

if __name__ == "__main__":
    socketio.run(app, debug=True)