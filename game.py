import gameengine as ge


# ge.draw()
ge.start_client()
print('Waiting for second player...')
server_answer = repr(ge.network.sock_obj.recv(1024))
if server_answer == 'starting':
    print('Starting the game!')
ge.draw()

stop = False

while not stop:
    data = repr(ge.network.sock_obj.recv(1024))

    if data == 'your-move':
        ge.draw()
        move = input('> ')
        while not ge.move(move):
            move = input('> ')
    if data == 'game-over':
        print('Game over!')
    if data == 'server-stop':
        print('Host broke down the connection')



