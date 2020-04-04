import sys
import gameengine as ge
from threading import Thread
from time import sleep


def abort():
    ge.stop_listener()
    sys.exit()


try:
    ge.start_client()
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
            print('You won!' if ge.network.player_symbol[2:-1] == data.split('|')[1] else 'You lost!')
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
        ge.update_table()
        ge.draw()
        sleep(0.1)

except KeyboardInterrupt:
    print('\nQuitting...')
    abort()



