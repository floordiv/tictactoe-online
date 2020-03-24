import gameengine as ge
from threading import Thread
from time import sleep


ge.start_client()

client_listener = Thread(target=ge.listen_client).start()

print('Waiting for connecting...')

while ge.network.data != 'starting':

    sleep(0.3)

print('Starting the game!')
ge.draw()


while True:
    data = ge.network.data

    if data == 'your-move':
        ge.draw()
        move = input('> ')
        while not ge.move(move):
            move = input('> ')
    if data == 'game-over':
        print('Game over!')
        break
    if data == 'server-stop':
        print('Host broke down the connection')
        break



