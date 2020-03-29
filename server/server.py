import socket
from datetime import datetime
from traceback import format_exc
from time import sleep
from termcolor import colored


debug = False


class network:
    sock_obj = None
    players = []
    players_sock_objs = []
    players_table = [i for i in range(1, 10)]


def currtime():
    return f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] '


def send(data):
    for conn in network.players_sock_objs:
        conn.send(bytes(data.encode('utf-8')))


def checkwin():
    win_poses = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                 (0, 3, 6), (1, 4, 7), (2, 5, 8),
                 (0, 4, 8), (2, 4, 6)]
    for pos in win_poses:
        players_at_areas = set([network.players_table[i] for i in pos])
        if len(players_at_areas) == 1:
            print(currtime() + colored(f'[SESSION] Player{1 if players_at_areas[0] == "x" else 2} has won!', 'blue'))
            send('game-over')


def wait_player(sock, player_index):
    conn, addr = sock.accept()
    client_details = repr(conn.recv(1024))[2:-1]
    print(currtime() + colored('[CONNECT] New connection from: ' + str(addr[0]) + ':' + str(addr[1]) + ' | ' + client_details, 'green'))
    network.players += [['x', 'o'][player_index]]
    network.players_sock_objs += [conn]
    conn.send(bytes(['x', 'o'][player_index].encode('utf-8')))


def stop_server(sock):
    print('\n' + currtime() + colored('[EXIT] Stopping server and closing socket...', 'red'))

    try:
        print(currtime() + colored('[EXIT] Sending stop-code to the clients', 'red'))
        send('server-stop')
    except Exception as sending_stop_code_exception:
        print(currtime() + colored('[EXIT] Failed to send stop-code to the clients: ' + str(sending_stop_code_exception), 'red'))
    sock.close()


def update_table():
    # print('updating table for clients:', ';'.join([str(i) for i in network.players_table]))
    for conn in network.players_sock_objs:
        conn.send(bytes(';'.join([str(i) for i in network.players_table]).encode('utf-8')))


def start(ip_address='127.0.0.1', on_port=8083):
    print(currtime() + '[INFO] Starting server on ip: ' + ip_address + ' on port: ' + str(on_port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.bind((ip_address, on_port))
        sock.listen(2)
        for i in range(2):
            wait_player(sock, i)
        print(currtime() + colored('[SESSION] Starting the game...', 'blue'))
        sleep(0.5)
        send('starting')
        # let the client handle with it
        sleep(0.5)
        while True:
            for i in range(2):
                client = network.players_sock_objs[i]

                print(currtime() + colored('[SESSION] Next player\'s move', 'blue'))
                try:
                    client.send(b'your-move')
                    sleep(0.3)
                    # update table for clients
                    update_table()
                except BrokenPipeError:
                    print(currtime() + colored(f'[SESSION] Player{i + 1} has disconnected', 'blue'))
                    wait_player(sock, i)
                    print(f'{currtime()}[SESSION] Player{i + 1} has connected again')
                    client = network.players_sock_objs[i]

                data = repr(client.recv(1024).decode('utf-8'))[1:-1]
                try:
                    network.players_table[int(data) - 1] = network.players[i]
                    print(
                        currtime() + colored(f'[SESSION] Received data from player{i + 1}: {data if data != "" else "<empty>"}', 'blue'))
                except:
                    if data == 'win':
                        send('game-over')
                        print(currtime() + colored('[SESSION] Winner is: player' + str(i + 1), 'blue'))
                        stop_server(sock)
                    else:
                        print(currtime() + colored(f'[ERROR] Received corrupted packet from player{i + 1}: {data if data != "" else "<empty>"}', 'red'))
                update_table()
                checkwin()
    except KeyboardInterrupt:
        stop_server(sock)
    except Exception as server_failure:
        if debug:
            print(format_exc())
        print(currtime() + colored('[SERVER-STOP] Uncaught error:' + str(server_failure), 'red'))
        stop_server(sock)


start()
