import sys
import json
import socket
import string
from time import sleep
from safecall import call
from random import choices
from threading import Thread
from datetime import datetime
from termcolor import colored
from traceback import format_exc

VERSION = '1.3.6'
MANUAL = False  # manual server control: start, end, etc. Can be imported as module
ASK_IP = True
ASK_PORT = True
DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 8083
USE_EXTERNAL_CONFIG = '--use-config' in sys.argv    # used for testing, but you can modify default config
EXTERNAL_CONFIG = 'server-conf.json'


def output(*text, splitter=' ', at_newline=False):
    if at_newline:
        print()

    out_types = {'info': data.info_color,
                 'exit': data.exit_color,
                 'error': data.err_color,
                 'session': data.session_color,
                 'connect': data.connect_color}

    currtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if text[0] in out_types:
        color = out_types[text[0]]
        print(colored(f'[{currtime}] [{str(text[0]).upper()}] {splitter.join([str(i) for i in text[1:]])}', color))
    else:
        print(f'[{currtime}]', splitter.join([str(i) for i in text]))


"""
network.rooms indexes:
 0, 1 - players' socket objects
 2 - table
 3 - room_id
 4 - room_status
"""


class network:
    rooms = []  # [player1 (sock obj), player2 (sock obj), players_table, room_id, status (not-started, running)]
    max_players = 10
    current_players = 0
    max_rooms = 6
    room_id_len = 6
    max_move_time = 10  # seconds. None for infinity

    sock = None


class data:
    threads = 0
    debug = True
    listener_timeout = 0.3
    exit_color = 'magenta'
    err_color = 'red'
    info_color = 'green'
    session_color = 'blue'
    connect_color = 'yellow'


class room:
    @staticmethod
    def generate_id():
        return ''.join(choices(string.ascii_letters, k=network.room_id_len))

    @staticmethod
    def find_by_id(room_id):
        room_obj = [i for i in network.rooms if i[3] == room_id]
        if len(room_obj) == 0:
            raise Warning('room not found: ' + room_id)
        return network.rooms.index(room_obj[0])     # returns index of the room

    @staticmethod
    def get(room_id):
        # if room is not found, room.find_by_id will raise warning as the lowest-level function
        return network.rooms[room.find_by_id(room_id)]

    @staticmethod
    def get_free():
        for _room in network.rooms:
            if None in _room[0:2]:
                return _room

    @staticmethod
    def is_full(room_id):
        return None not in room.get(room_id)[0:2]

    @staticmethod
    def players_in_room(room_id):
        return 2 - room.get(room_id)[0:2].count(None)

    @staticmethod
    def create():
        room_id = room.generate_id()
        if len(network.rooms) < network.max_rooms:
            network.rooms.append([None, None, [str(i) for i in range(1, 10)], room_id, 'not-started'])
            return room_id
        raise Warning('max rooms count has been reached')

    @staticmethod
    def add_player(room_id, obj):   # obj - player obj
        room_obj = room.get(room_id)
        if None not in room_obj:
            raise Warning('room is already full')
        first_none_index = room_obj.index(None)     # if there is one player, the second will be placed
        room_obj[first_none_index] = obj

    @staticmethod
    def remove_player(room_id, player_index):
        room.get(room_id)[player_index] = None

    @staticmethod
    def set_status(room_id, new_status):
        room.get(room_id)[4] = new_status

    @staticmethod
    def stop(room_id, send_code=True):
        if send_code:
            net.send(room_id, 'room-closed', debug_print_on_brokenpipe=False)
        network.current_players -= room.players_in_room(room_id)
        data.threads -= 1
        del network.rooms[room.find_by_id(room_id)]


class game:
    @staticmethod
    def update_table(room_id, updated_cell, player_letter):
        room.get(room_id)[2][updated_cell] = player_letter

    @staticmethod
    def checkwin(room_id):
        win_poses = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                     (0, 3, 6), (1, 4, 7), (2, 5, 8),
                     (0, 4, 8), (2, 4, 6)]
        free_cells = [i for i in room.get(room_id)[2] if i.isdigit()]
        if len(free_cells) == 0:    # draw
            sleep(0.3)
            net.send(room_id, 'game-over|draw')
            return True
        for pos in win_poses:
            players_at_areas = list(set([room.get(room_id)[2][i] for i in pos]))
            if len(players_at_areas) == 1:
                # win
                sleep(0.3)
                net.send(room_id, 'game-over|' + players_at_areas[0])
                return True
        return False

    @staticmethod
    def start(room_id):
        # TODO: listen both clients at the moment
        if room.is_full(room_id):   # run
            sleep(0.3)
            net.send(room_id, 'starting')
            sleep(0.4)

            if network.max_move_time is not None:
                for player in room.get(room_id)[0:2]:
                    player.settimeout(network.max_move_time)
                net.send(room_id, f'Time per move is limited: {network.max_move_time} seconds')
                sleep(0.3)
            else:
                net.send('<empty>')

            while True:
                for i in range(2):
                    try:
                        conn = call(room.get, args=(room_id,), errs=Warning)

                        if conn is None:
                            output('error', 'Trying to get not existing room:', room_id)
                            room.stop(room_id)
                            return

                        conn = conn[i]

                        try:
                            conn.send('your-move'.encode('utf-8'))
                        except BrokenPipeError:
                            output('session', f'{room_id}: player{i + 1} has disconnected. Destroying the room...')
                            room.stop(room_id)
                            return   # exit from thread

                        sleep(0.31)
                        net.update_table(room_id)

                        try:
                            received = conn.recv(1024).decode('utf-8')
                        except socket.timeout:
                            output('session', f'{room_id}#player{i + 1} is not responding for a long time. Destroying '
                                              'the room...')
                            net.send(room_id, 'game-over|' + 'x' if i == 1 else 'o')
                            room.stop(room_id, send_code=False)
                            return

                        if received.strip() in ['', 'disconnected']:  # player has disconnected
                            output('session', f'{room_id}#player{i + 1} has disconnected. Destroying room...')
                            conn.send(f'game-over|{"x" if i == 0 else "o"}'.encode('utf-8'))
                            room.stop(room_id)
                            return

                        packet_is_corrupted = call(game.update_table, args=(room_id, int(received) - 1, ['x', 'o'][i]),
                                                   errs=(TypeError, ValueError), on_catch=True)
                        if packet_is_corrupted:
                            output('error', f'Received corrupted packet from {room_id}#player{i + 1}: {received if received != "" else "<empty>"}')
                            room.stop(room_id)
                            return

                        net.update_table(room_id)
                        win_detected = game.checkwin(room_id)

                        if win_detected:
                            output('session', f'{room_id}: winner is player{i + 1}. Destroying room...')
                            sleep(0.3)
                            room.stop(room_id, send_code=False)
                            return
                    except Exception as debug_info:
                        output('error', f'An error occurred for {room_id}#player{i + 1}: {debug_info}')
                        if data.debug:
                            print(colored(format_exc(), data.err_color))
                        room.stop(room_id)
                        return


class server:
    @staticmethod
    def start(ip=DEFAULT_IP, port=DEFAULT_PORT):    # listener and rooms/connects handler (main function)
        output('info', f'Tic Tac Toe Online server, version {VERSION}. Starting...')
        network.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        output('info', f'Using ip:port: {ip}:{port}')
        if USE_EXTERNAL_CONFIG:
            output('info', f'Using external config: {EXTERNAL_CONFIG}. Loading config...')

            with open(EXTERNAL_CONFIG, 'r') as conf:
                conf = json.load(conf)[0]

            for conf_type in ['network', 'data']:
                if conf_type in conf:
                    network_vars = conf[conf_type]

                    for var in network_vars:
                        # I know, that using eval is a shitcode. But, I wanted to do it by only the one loop, so...
                        # let it be (don't hit me too much)
                        setattr(eval(conf_type), var, network_vars[var])

            output('info', f'Loading settings from {EXTERNAL_CONFIG} has been completed')

        sock_is_in_use = call(network.sock.bind, args=((ip, port),), errs=OSError, on_catch=True)
        if sock_is_in_use:
            output('error', f'Unable to bind {ip}:{port}: already in use')
            exit()

        output('info', 'Max players:', network.max_players)
        output('info', 'Max rooms:', network.max_rooms)
        network.sock.listen(network.max_players)
        output('info', f'Server successfully initialized. Starting listener...')

        try:
            while True:
                conn, addr = network.sock.accept()

                net.remove_disconnected_players()

                if network.current_players < network.max_players and len(network.rooms) < network.max_rooms:
                    client_details = conn.recv(1024).decode('utf-8')
                    output('connect', f'New connection from {addr[0]}:{addr[1]}, {client_details}')

                    if network.current_players % 2 == 0:    # create new room
                        room_id = call(room.create, errs=Warning, on_catch=None)

                        if room_id is None:     # max rooms count has been reached
                            # it shouldn't happen because of if expression, but everything is possible
                            conn.send('disconnected'.encode('utf-8'))

                            continue

                        output('info', 'Created new room:', room_id)
                    else:
                        room_id = room.get_free()[3]
                        output('info', 'Adding player to the existing room:', room_id)

                    network.current_players += 1

                    try:
                        player_letter = ['x', 'o'][room.players_in_room(room_id)]
                        room.add_player(room_id, conn)
                        conn.send(player_letter.encode('utf-8'))
                        sleep(0.3)
                        conn.send(room_id.encode('utf-8'))
                    except BrokenPipeError:
                        players_in_room = room.players_in_room(room_id)
                        if players_in_room == 2:
                            new_room_id_for_player = room.create()
                            room.add_player(new_room_id_for_player, room.get(new_room_id_for_player)[0])
                        room.stop(room_id)

                    not_started_rooms = [i for i in network.rooms if i[4] == 'not-started' and room.is_full(i[3])]

                    # start all rooms
                    for not_started_room in not_started_rooms:

                        room_id = not_started_room[3]

                        output('info', 'Starting room:', room_id)

                        room_thread = Thread(target=game.start, args=(room_id,), daemon=True)
                        data.threads += 1
                        room.set_status(room_id, 'running')
                        room_thread.start()
                else:
                    conn.send('server-is-busy'.encode('utf-8'))
                    conn.close()

                sleep(data.listener_timeout)
        except KeyboardInterrupt:
            server.stop()

    @staticmethod
    def stop():
        output('exit', 'Sending stop-code to players...', at_newline=True)
        net.send('server-stop')
        sleep(0.31)
        output('exit', 'Closing socket...')
        network.sock.close()
        sys.exit()


class net:
    @staticmethod
    def send(*args, debug_print_on_brokenpipe=True):
        if len(args) == 1:  # broadcast
            for each in [i[0:2] for i in network.rooms]:
                for conn in each:
                    if conn is not None:
                        call(conn.send, args=(args[0].encode('utf-8'),), errs=BrokenPipeError)
        else:   # send to both clients
            room_id, data_to_send = args
            for index, conn in enumerate([i for i in room.get(room_id)[0:2]]):
                try:
                    conn.send(bytes(data_to_send.encode('utf-8')))
                except BrokenPipeError:
                    if debug_print_on_brokenpipe:
                        output('error', f'Unable to send data to {room_id}#player{index + 1}: connection is broken')

    @staticmethod
    def update_table(room_id):
        net.send(room_id, ';'.join(room.get(room_id)[2]))

    @staticmethod
    def remove_disconnected_players():
        disconnected = 0
        output('info', 'Removing disconnected players...')

        for _room in network.rooms:
            for index, player in enumerate(_room[0:2]):
                if player is not None:
                    try:
                        player.send('disconnect-check'.encode('utf-8'))
                    except BrokenPipeError:  # found a disconnected player
                        disconnected += 1
                        output('info', f'Disconnecting {_room[3]}#player{index + 1}...')
                        room.remove_player(_room[3], index)
        return disconnected


if not MANUAL:
    _ip, _port = DEFAULT_IP, DEFAULT_PORT
    if ASK_IP:
        _ip = input(f'Bind ip (press enter for default: {_ip})> ')
        if len(_ip.strip()) == 0:    # use default ip
            _ip = DEFAULT_IP

    if ASK_PORT:
        _port = input(f'Bind port (press enter for default: {_port})> ')
        if len(_port.strip()) == 0:    # use default port
            _port = DEFAULT_PORT

    server.start(ip=_ip, port=_port)

