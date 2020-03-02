import socket


class network:
    sock_obj = None
    players = []
    players_sock_objs = []
    players_table = [i for i in range(1, 10)]


def start(on_port=8083):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.bind(('127.0.0.1', on_port))
        sock.listen(2)
        for i in range(2):
            conn, addr = sock.accept()
            client_details = repr(conn.recv(1024))
            print('Connection:', addr, '|', client_details)
            network.players += [['x', 'o'][i]]
            network.players_sock_objs += [conn]
            conn.send(bytes(['x', 'o'][i].encode('utf-8')))
        sock.sendall(b'starting')
        while True:
            for i in range(2):
                client = network.players_sock_objs[i]
                client.send(b'your-move')
                data = repr(client.recv(1024))
                try:
                    network.players_table[int(data)] = network.players[i]
                except:
                    if data == 'win':
                        sock.sendall(b'game-over')
                        print('Winner is player', i + 1)
                        sock.close()
                        return
                    else:
                        print(f'[ERROR] Received corrupted packet from {client}: {data}')
                network.sock_obj.sendall(bytes(';'.join([str(i) for i in network.players_table]).encode('utf-8')))
    except KeyboardInterrupt:
        sock.sendall(b'server-stop')
        sock.close()


start()
