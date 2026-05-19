import socket

server = socket.socket()
server.bind(("0.0.0.0", 5555))
server.listen(2)   # allow 2 players

print("Waiting for players...")

conn1, addr1 = server.accept()
print("Player 1 connected")

conn2, addr2 = server.accept()
print("Player 2 connected")

# send welcome messages


board = [" " for _ in range(9)]

def show_board(b):
    return (
        f"{b[0]} | {b[1]} | {b[2]}\n"
        f"---------\n"
        f"{b[3]} | {b[4]} | {b[5]}\n"
        f"---------\n"
        f"{b[6]} | {b[7]} | {b[8]}"
    )

# send initial board
conn1.send(("You are Player 1 (X)\n\n" + show_board(board)).encode())
conn2.send(("You are Player 2 (O)\n\n" + show_board(board)).encode())


def check_winner(b):
    wins = [(0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)]

    for x, y, z in wins:
        if b[x] == b[y] == b[z] and b[x] != " ":
            return b[x]

    return None


while True:
    # PLAYER 1 TURN
    conn1.send("Your move (0-8): ".encode())
    move1 = int(conn1.recv(1024).decode())

    if board[move1] != " ":
        conn1.send("Invalid move! Try again.\n".encode())
        continue

    board[move1] = "X"

    conn1.send(show_board(board).encode())
    conn2.send(show_board(board).encode())

    winner = check_winner(board)
    if winner:
        conn1.send("You win! 🎉".encode())
        conn2.send("You lose 😢".encode())
        break

    if " " not in board:
        conn1.send("It's a draw!".encode())
        conn2.send("It's a draw!".encode())
        break

    # PLAYER 2 TURN
    conn2.send("Your move (0-8): ".encode())
    move2 = int(conn2.recv(1024).decode())

    if board[move2] != " ":
        conn2.send("Invalid move! Try again.\n".encode())
        continue

    board[move2] = "O"

    conn1.send(show_board(board).encode())
    conn2.send(show_board(board).encode())

    winner = check_winner(board)
    if winner:
        conn2.send("You win! 🎉".encode())
        conn1.send("You lose 😢".encode())
        break

    if " " not in board:
        conn1.send("It's a draw!".encode())
        conn2.send("It's a draw!".encode())
        break

