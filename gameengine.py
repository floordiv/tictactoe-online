import socket
import platform
from time import sleep
from os import system, abort


cls = 'cls' if platform.system().lower() == 'windows' else 'clear'


class network:
    sock_obj = None
    players_table = [str(i) for i in range(1, 10)]
    player_symbol = 'x'
    data = ''


def listen_client():
    if network.sock_obj is None:
        print('[WARNING] Client was not started! Starting again...')
        start_client()
    while True:
        try:
            network.data = repr(network.sock_obj.recv(1024).decode('utf-8'))[1:-1]
        except ConnectionResetError:
            print('[ERROR] Server reset connection')
            abort()


def start_client(server='127.0.0.1:8083'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip, port = server.split(':')
    sock.connect((ip, int(port)))
    sock.send(bytes(f'client information: {platform.system()}, {platform.platform()}, {platform.processor()}'.encode('utf-8')))
    network.sock_obj = sock
    network.player_symbol = repr(sock.recv(1024))

    return sock


def send_data(data):
    try:
        network.sock_obj.send(bytes(str(data).encode('utf-8')))
    except BrokenPipeError:
        print('[ERROR] Server has closed the connection')


def move(coord):
    if coord in network.players_table and network.players_table[int(coord) - 1].isdigit():
        network.players_table[int(coord) - 1] = network.player_symbol
        # input(str(network.players_table))
    else:
        return False
    send_data(coord)
    while network.data == 'your-move':
        sleep(0.3)
    update_table()
    draw()
    return True


def new_table_is_not_downgrade(table):
    network_table_nums = [i for i in network.data.split(';') if i.isdigit()]
    return len(network_table_nums) < len([i for i in table if i.isdigit()])


def update_table():
    sleep(0.2)
    table = [i for i in network.data.split(';')]
    if len(table) == 9 and not new_table_is_not_downgrade(table):
        network.players_table = table


def draw():
    system(cls)
    print('-' * 13)
    for i in range(9):  # lines
        if i % 3 == 0 and i not in [0, 1]:  # new line
            print('|\n' + '-' * 13)
        print(f'| {network.players_table[i]}', end=' ')
    print('|')
    print('-' * 13)
