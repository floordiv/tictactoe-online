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

print('Waiting for second player...')

try:
    while ge.network.data not in ['starting', 'your-move']:
        sleep(0.3)

    print('Starting the game!')
    ge.draw()

    while True:
        data = ge.network.data

        if data == 'your-move':
            print('LALALALALALALAL')
            sleep(0.1)
            # sleep(1)
            ge.update_table()
            ge.draw()
            move = input('cell index [1-9]> ')
            while True:
                answer = ge.move(move)
                if answer:
                    break
                move = input('enter valid number [1-9]> ')
            ge.draw()
        elif data == 'game-over':
            print('Game over!')
            break
        elif data == 'server-stop':
            print('Host has broke down the connection')
            break
        else:
            print(data)
        sleep(0.1)

except KeyboardInterrupt:
    print('\nQuitting...')
    abort()



