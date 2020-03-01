import socket
import platform


class network:
    sock_obj = None
    players_table = [i for i in range(1, 10)]
    player_symbol = 'x'


def start_client(server='127.0.0.1:8083'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip, port = server.split(':')
    # sock.bind((ip, int(port)))
    sock.connect((ip, int(port)))
    sock.send(bytes(f'connection: {platform.system()}, {platform.platform()}, {platform.processor()}'))
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
    network.players_table = [int(i) for i in repr(network.sock_obj.recv(1024)).split(';')]
    draw()


def draw():
    print('-' * 13)
    for i in range(9):  # lines
        if i % 3 == 0 and i not in [0, 1]:  # new line
            print('|\n' + '-' * 13)
        print(f'| {network.players_table[i]}', end=' ')
    print('|')
    print('-' * 13)
