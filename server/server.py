import socket
from datetime import datetime
from traceback import format_exc


debug = True


class network:
    sock_obj = None
    players = []
    players_sock_objs = []
    players_table = [i for i in range(1, 10)]


def currtime():
    return f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] '


def start(ip_address='127.0.0.1', on_port=8083):
    print(currtime() + '[INFO] Starting server on ip:', ip_address, 'on port:', on_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.bind((ip_address, on_port))
        sock.listen(2)
        for i in range(2):
            conn, addr = sock.accept()
            client_details = repr(conn.recv(1024))[2:-1]
            print(currtime() + '[CONNECT] New connection from:', addr[0] + ':' + addr[1], '|', client_details)
            network.players += [['x', 'o'][i]]
            network.players_sock_objs += [conn]
            conn.send(bytes(['x', 'o'][i].encode('utf-8')))
        print(currtime() + '[SESSION] Starting the game...')
        for conn in network.players_sock_objs:
            conn.send(b'starting')
        # sock.sendall(b'starting')
        while True:
            for i in range(2):
                client = network.players_sock_objs[i]
                print(currtime() + '[SESSION] Next player\'s move')
                client.send(b'your-move')
                data = repr(client.recv(1024))
                try:
                    network.players_table[int(data)] = network.players[i]
                except:
                    if data == 'win':
                        sock.sendall(b'game-over')
                        print(currtime() + '[SESSION] Winner is: player', i + 1)
                        sock.close()
                        return
                    else:
                        print(f'{currtime()}[ERROR] Received corrupted packet from {client}: {data}')
                network.sock_obj.sendall(bytes(';'.join([str(i) for i in network.players_table]).encode('utf-8')))
    except Exception as server_failure:
        if debug:
            print(format_exc())
        print(currtime() + '[SERVER-STOP] Uncaught error:', server_failure)
        try:
            print(currtime() + '[EXIT] Sending stop-code to the clients')
            for conn in network.players_sock_objs:
                conn.send(b'server-stop')
        except Exception as sending_stop_code_exception:
            print(currtime() + '[EXIT] Failed to send stop-code to the clients:', sending_stop_code_exception)
        print(currtime() + '[EXIT] Closing socket...')
        sock.close()


start()
