import os
import sys
import gameengine as ge
from time import sleep
from threading import Thread


ip, port = '127.0.0.1', 8083


if len(sys.argv) == 2:
    ip, port = sys.argv[1].split(':')


def abort():
    ge.stop_listener()
    os.abort()


try:
    ge.start_client(ip, port)
except ConnectionRefusedError:
    print('[ERROR] Server is unavailable')
    exit()

client_listener = Thread(target=ge.listen_client).start()

print('Waiting for second player...')

try:
    while ge.network.data not in ['starting', 'your-move']:
        sleep(0.3)

    print('Starting the game!')
    ge.draw()

    while True:
        data = ge.network.data
        ge.draw()

        if data == 'your-move':
            sleep(0.1)
            ge.update_table()
            ge.draw()
            move = input('cell index [1-9]> ')
            while True:
                answer = ge.move(move)
                if answer:
                    break
                move = input('enter valid number [1-9]> ')
        elif data.split('|')[0] == 'game-over':
            ge.draw()
            print('You won!' if ge.network.player_symbol == data.split('|')[1] else 'You lost!')
            abort()
        elif data.strip() == '':    # server close, it can be as a gameover
            ge.draw()
            print('You lost!')
            abort()
        elif data == 'server-stop':
            print('Host has broke down the connection')
            abort()
        elif data == 'room-closed':
            print('Room has been destroyed: second player has disconnected')
            abort()
        ge.update_table()
        ge.draw()
        sleep(0.1)

except KeyboardInterrupt:
    print('\nQuitting...')
    abort()



