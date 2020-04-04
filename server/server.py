import socket
from datetime import datetime
from traceback import format_exc
from time import sleep
from termcolor import colored


VERSION = '0.1.0'

debug = False

exit_color = 'magenta'
err_color = 'red'
info_color = 'grey'
session_color = 'blue'
connect_color = 'green'


class network:
    sock_obj = None
    players = []
    players_sock_objs = []
    players_table = [i for i in range(1, 10)]


def currtime():
    return f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] '


def send(data):
    for conn in network.players_sock_objs:
        conn.send(data.encode('utf-8'))


def checkwin(sock):
    win_poses = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                 (0, 3, 6), (1, 4, 7), (2, 5, 8),
                 (0, 4, 8), (2, 4, 6)]
    for pos in win_poses:
        players_at_areas = list(set([network.players_table[i] for i in pos]))
        if len(players_at_areas) == 1:
            print(currtime() + colored(f'[SESSION] Player{1 if players_at_areas[0] == "x" else 2} has won!', session_color))
            update_table()
            sleep(0.5)
            send(f'game-over|{players_at_areas[0]}')
            sleep(0.5)
            stop_server(sock, force_exit=True)


def wait_player(sock, player_index):
    conn, addr = sock.accept()
    client_details = conn.recv(1024).decode('utf-8')
    print(currtime() + colored('[CONNECT] New connection from: ' + str(addr[0]) + ':' + str(addr[1]) + ' | ' + client_details, connect_color))
    network.players += [['x', 'o'][player_index]]
    network.players_sock_objs += [conn]
    conn.send(['x', 'o'][player_index].encode('utf-8'))
    sleep(0.3)
    conn.send('not supported by server'.encode('utf-8'))


def stop_server(sock, force_exit=False):
    print('\n' + currtime() + colored('[EXIT] Stopping server and closing socket...', exit_color))

    try:
        print(currtime() + colored('[EXIT] Sending stop-code to the clients', exit_color))
        send('server-stop')
    except Exception as sending_stop_code_exception:
        print(currtime() + colored('[EXIT] Failed to send stop-code to the clients: ' + str(sending_stop_code_exception), exit_color))
    sock.close()
    if force_exit:
        exit()


def update_table():
    # print('updating table for clients:', ';'.join([str(i) for i in network.players_table]))
    for conn in network.players_sock_objs:
        conn.send(';'.join([str(i) for i in network.players_table]).encode('utf-8'))


def start(ip_address='127.0.0.1', on_port=8083):
    print(f'{currtime()}[INFO] Starting server on ip: {ip_address}; on port: {on_port}; server-version: {VERSION}')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.bind((ip_address, on_port))
        sock.listen(2)
        for i in range(2):
            wait_player(sock, i)
        print(currtime() + colored('[SESSION] Starting the game...', session_color))
        sleep(0.5)
        send('starting')
        # let the client handle with it
        sleep(0.5)
        while True:
            for i in range(2):
                # checkwin(sock)
                client = network.players_sock_objs[i]

                print(currtime() + colored(f'[SESSION] Player{i + 1}\'s move', session_color))
                try:
                    client.send('your-move'.encode('utf-8'))
                    # sleep, because client may pass it threw because of timings
                    sleep(0.3)
                    # update table for clients
                    update_table()
                except BrokenPipeError:
                    print(currtime() + colored(f'[SESSION] Player{i + 1} has disconnected', session_color))
                    wait_player(sock, i)
                    print(f'{currtime()}[SESSION] Player{i + 1} has connected again')
                    client = network.players_sock_objs[i]

                data = client.recv(1024).decode('utf-8')
                try:
                    network.players_table[int(data) - 1] = network.players[i]
                    print(
                        currtime() + colored(f'[SESSION] Received data from player{i + 1}: {data if data != "" else "<empty>"}', session_color))
                except:
                    print(currtime() + colored(f'[ERROR] Received corrupted packet from player{i + 1}: {data if data != "" else "<empty>"}', err_color))
                update_table()
                checkwin(sock)
    except KeyboardInterrupt:
        stop_server(sock)
    except Exception as server_failure:
        if debug:
            print(format_exc())
        print(currtime() + colored('[SERVER-STOP] Uncaught error:' + str(server_failure), err_color))
        stop_server(sock)


start()
