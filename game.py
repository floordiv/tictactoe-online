import gameengine as ge
from threading import Thread
from time import sleep


client_listener = Thread(target=ge.listen_client)


ge.start_client()
print('Waiting for second player...')
server_answer = ge.network.data
while server_answer != 'starting':
    sleep(0.3)
print('Starting the game!')
ge.draw()

stop = False

while not stop:
    data = ge.network.data

    if data == 'your-move':
        ge.draw()
        move = input('> ')
        while not ge.move(move):
            move = input('> ')
    if data == 'game-over':
        print('Game over!')
    if data == 'server-stop':
        print('Host broke down the connection')



