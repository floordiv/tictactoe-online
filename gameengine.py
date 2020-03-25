import socket
import platform
from os import system


cls = 'cls' if platform.system().lower() == 'windows' else 'clear'


class network:
    sock_obj = None
    players_table = [i for i in range(1, 10)]
    player_symbol = 'x'
    data = ''


def listen_client():
    if network.sock_obj is None:
        print('[WARNING] Client was not started!')
        start_client()
    while True:
        network.data = repr(network.sock_obj.recv(1024))[2:-1]
        print(network.data, True)


def start_client(server='127.0.0.1:8083'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip, port = server.split(':')
    # sock.bind((ip, int(port)))
    sock.connect((ip, int(port)))
    sock.send(bytes(f'client information: {platform.system()}, {platform.platform()}, {platform.processor()}'.encode('utf-8')))
    network.sock_obj = sock
    network.player_symbol = repr(sock.recv(1024))

    return sock


def send_data(data):
    network.sock_obj.send(bytes(data))


def move(coord):
    if coord in network.players_table:
        network.players_table[network.players_table.index(coord)] = network.player_symbol
    else:
        return False
    send_data(coord)
    network.players_table = [int(i) for i in network.data.split(';')]
    draw()


def draw():
    system(cls)
    print('-' * 13)
    for i in range(9):  # lines
        if i % 3 == 0 and i not in [0, 1]:  # new line
            print('|\n' + '-' * 13)
        print(f'| {network.players_table[i]}', end=' ')
    print('|')
    print('-' * 13)
