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
    stop_listener = False

    server_test_codes = ['disconnect-check']


def listen_client():
    if network.sock_obj is None:
        print('[WARNING] Client was not started! Starting again...')
        start_client('127.0.0.1', 8083)
    while True:
        if network.stop_listener:
            network.sock_obj.close()
            exit()
        try:
            data = network.sock_obj.recv(1024).decode('utf-8')
            if data not in network.server_test_codes:
                network.data = data
            else:
                network.sock_obj.send('echo'.encode('utf-8'))
        except ConnectionResetError:
            print('[ERROR] Server reset connection')
            abort()


def start_client(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.send(f'client information: {platform.system()}, {platform.platform()}, {platform.processor()}'.encode('utf-8'))
    network.sock_obj = sock
    try:
        network.player_symbol = sock.recv(1024).decode('utf-8')

        if network.player_symbol == 'disconnected':
            print('[ERROR] Disconnected by server')
            exit()
        elif network.player_symbol == 'server-is-busy':
            print('[ERROR] Server is unavailable now, please, try to connect later')
            abort()
    except ConnectionRefusedError:
        print('[ERROR] Server refused connection')
        exit()
    try:
        print('[SESSION] Room id:', sock.recv(1024).decode('utf-8'))
    except KeyboardInterrupt:
        abort()

    return sock


def send_data(data):
    try:
        network.sock_obj.send(str(data).encode('utf-8'))
    except BrokenPipeError:
        print('[ERROR] Server has closed the connection')
        abort()


def move(coord):
    if coord in network.players_table and network.players_table[int(coord) - 1].isdigit():
        network.players_table[int(coord) - 1] = network.player_symbol
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


def players_table_symbols_are_valid():
    return len(set([len(i) for i in network.players_table])) == 1


def fix_table():    # when player won/lost, network.player_symbol becomes byte-like (idk why)
    if not players_table_symbols_are_valid():
        network.players_table = [i if len(i) == 1 else i[2:-1] for i in network.players_table]


def update_table():
    sleep(0.2)
    table = [i for i in network.data.split(';')]
    if len(table) == 9 and not new_table_is_not_downgrade(table):
        network.players_table = table
        return True


def stop_listener():
    network.stop_listener = True
    network.sock_obj.close()


def draw():
    fix_table()
    system(cls)
    print('-' * 13)
    for i in range(9):  # lines
        if i % 3 == 0 and i not in [0, 1]:  # new line
            print('|\n' + '-' * 13)
        print(f'| {network.players_table[i]}', end=' ')
    print('|')
    print('-' * 13)
