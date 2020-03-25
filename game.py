import gameengine as ge
from threading import Thread
from time import sleep


try:
    ge.start_client()
except ConnectionRefusedError:
    print('[ERROR] Server is unavailable')
    exit()

client_listener = Thread(target=ge.listen_client).start()

print('Waiting for connecting...')

try:
    while ge.network.data != 'starting':

        sleep(0.3)

    print('Starting the game!')
    ge.draw()

    while True:
        data = ge.network.data

        print(data)

        if data == 'your-move':
            print('lalalalala')
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
except KeyboardInterrupt:
    print('Quitting...')
    exit()



