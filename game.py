import gameengine as ge
from threading import Thread
from time import sleep
from os import abort


try:
    ge.start_client()
except ConnectionRefusedError:
    print('[ERROR] Server is unavailable')
    exit()

client_listener = Thread(target=ge.listen_client).start()

print('Waiting for connecting second player...')

try:
    while ge.network.data not in ['starting', 'your-move']:
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
        elif data == 'game-over':
            print('Game over!')
            break
        elif data == 'server-stop':
            print('Host has broke down the connection')
            break
except KeyboardInterrupt:
    print('\nQuitting...')
    abort()



