import socket
from datetime import datetime
from traceback import format_exc


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


def wait_player(sock, player_index):
    conn, addr = sock.accept()
    client_details = repr(conn.recv(1024))[2:-1]
    print(currtime() + '[CONNECT] New connection from:', str(addr[0]) + ':' + str(addr[1]), '|', client_details)
    network.players += [['x', 'o'][player_index]]
    network.players_sock_objs += [conn]
    conn.send(bytes(['x', 'o'][player_index].encode('utf-8')))


def stop_server(sock):
    print('\n' + currtime() + '[EXIT] Stopping server and closing socket...')

    try:
        print(currtime() + '[EXIT] Sending stop-code to the clients')
        send('server-stop')
    except Exception as sending_stop_code_exception:
        print(currtime() + '[EXIT] Failed to send stop-code to the clients:', sending_stop_code_exception)
    print(currtime() + '[EXIT] Closing socket...')
    sock.close()


def start(ip_address='127.0.0.1', on_port=8083):
    print(currtime() + '[INFO] Starting server on ip:', ip_address, 'on port:', on_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.bind((ip_address, on_port))
        sock.listen(2)
        for i in range(2):
            wait_player(sock, i)
        print(currtime() + '[SESSION] Starting the game...')
        send('starting')
        # sock.sendall(b'starting')
        while True:
            for i in range(2):
                client = network.players_sock_objs[i]
                print(currtime() + '[SESSION] Next player\'s move')
                try:
                    client.send(b'your-move')
                except BrokenPipeError:
                    print(f'{currtime()}[SESSION] Player{i + 1} has disconnected')
                    wait_player(sock, i)
                    print(f'{currtime()}[SESSION] Player{i + 1} has connected again')
                    client = network.players_sock_objs[i]

                data = repr(client.recv(1024).decode('utf-8'))[1:-1]
                try:
                    network.players_table[int(data) - 1] = network.players[i]
                    print(
                        f'{currtime()}[SESSION] Received data from player{i + 1}: {data if data != "" else "<empty>"}')
                except:
                    if data == 'win':
                        send('game-over')
                        print(currtime() + '[SESSION] Winner is: player', i + 1)
                        sock.close()
                        return
                    else:
                        print(f'{currtime()}[ERROR] Received corrupted packet from player{i + 1}: {data if data != "" else "<empty>"}')
                for conn in network.players_sock_objs:
                    conn.send(bytes(';'.join([str(i) for i in network.players_table]).encode('utf-8')))
    except KeyboardInterrupt:
        stop_server(sock)
    except Exception as server_failure:
        if debug:
            print(format_exc())
        print(currtime() + '[SERVER-STOP] Uncaught error:', server_failure)
        stop_server(sock)


start()
