# peace of shitcode, which is not working. Do not look here!

# import sys
# import socket
# import string
# import ctypes
# import threading
# from time import sleep
# from random import choices
# from threading import Thread
# from datetime import datetime
# from termcolor import colored
# from traceback import format_exc
#
# VERSION = '1.0.0'
#
# debug = True
#
# err_color = 'red'
# info_color = 'grey'
# exit_color = 'magenta'
# session_color = 'blue'
# connect_color = 'green'
#
#
# class network:
#     sock = None
#     players = []
#     players_table = [i for i in range(1, 10)]
#     rooms = []  # [player1 (sock obj), player2 (sock obj), players_table, room_id, status (not-started, running)]
#     room_id_len = 5
#     max_players = 10  # max rooms is max_players / 2
#     players_online = 0
#
#
# class data:
#     threads = []
#
#
# class thread(Thread):
#     def __init__(self, name, target=None, args=(), kwargs={}):
#         threading.Thread.__init__(self)
#         self.name = name
#         self.target = target
#         self.args = args
#         self.kwargs = kwargs
#
#     def run(self):
#
#         # target function of the thread class
#         try:
#             self.target(*self.args, **self.kwargs)
#         finally:
#             print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + colored(' [EXIT] Stopping thread...'), exit_color)
#
#     def get_id(self):
#
#         # returns id of the respective thread
#         if hasattr(self, '_thread_id'):
#             return self._thread_id
#         for id, thread in threading._active.items():
#             if thread is self:
#                 return id
#
#     def stop(self):
#         thread_id = self.get_id()
#         res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
#                                                          ctypes.py_object(SystemExit))
#         if res > 1:
#             ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
#
#
# def currtime():
#     return f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] '
#
#
# def send(*args):
#     if len(args) == 1:
#         for each in [i[0:2] for i in network.rooms]:
#             for conn in each:
#                 conn.send(bytes(args[0].encode('utf-8')))
#     else:
#         room_id, data = args
#         for conn in [i[0:2] for i in network.rooms[find_room_by_id(room_id)]]:
#             conn.send(bytes(data.encode('utf-8')))
#
#
# def checkwin(room_id):
#     win_poses = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
#                  (0, 3, 6), (1, 4, 7), (2, 5, 8),
#                  (0, 4, 8), (2, 4, 6)]
#     for pos in win_poses:
#         players_at_areas = list(set([network.players_table[i] for i in pos]))
#         if len(players_at_areas) == 1:
#             print(currtime() + colored(f'[SESSION] Player{1 if players_at_areas[0] == "x" else 2} has won!',
#                                        session_color))
#             update_table(room_id)
#             sleep(0.5)
#             send(f'game-over|{players_at_areas[0]}')
#             sleep(0.5)
#             # stop_room(force_exit=True)
#             stop_room(room_id)
#
#
# def generate_room_id():
#     return ''.join(choices(string.ascii_letters, k=network.room_id_len))
#
#
# def create_room():
#     room_id = generate_room_id()
#     network.rooms.append([None, None, [i for i in range(1, 10)], room_id, 'not-started'])
#     print(network.rooms)
#     return room_id
#
#
# def find_room_by_id(room_id):
#     room_obj = [i for i in network.rooms if i[3] == room_id]
#     if len(room_obj) == 0:
#         return None
#     return network.rooms.index(room_obj[0])
#
#
# def rooms_are_full():
#     return bool(len(network.rooms) - len([i for i in network.rooms if len(i) == 4]))
#
#
# def edit_room(room_id, player1=None, player2=None):
#     room_index = find_room_by_id(room_id)
#     if room_index is None:
#         print(currtime() + colored('[ERROR] Editing not existing room!', err_color))
#         return
#     for index, element in enumerate([player1, player2]):
#         if element is not None:
#             network.rooms[room_index][index] = element
#     # stop_room(room_id)
#
#
# def delete_room(room_id):
#     room_index = find_room_by_id(room_id)
#     if room_index is not None:
#         del network.rooms[room_index]
#
#
# def connects_listener():
#     try:
#         network.sock.listen(network.max_players)
#         temp_room_id = ''
#         while True:
#             player_index = 1
#             if rooms_are_full() or len(network.rooms) == 0:
#                 room_id = create_room()  # creates room and returns room_id
#                 temp_room_id = room_id
#                 player_index = 0
#             conn, addr = network.sock.accept()
#             network.players_online += 1
#             if player_index == 0:
#                 edit_room(temp_room_id, player1=conn)
#             else:
#                 edit_room(temp_room_id, player2=conn)
#             client_details = repr(conn.recv(1024))[2:-1]
#             print(currtime() + colored(
#                 '[CONNECT] New connection from: ' + str(addr[0]) + ':' + str(addr[1]) + ' | ' + client_details,
#                 connect_color))
#             conn.send(bytes(['x', 'o'][player_index].encode('utf-8')))
#             sleep(0.3)
#             conn.send(bytes(temp_room_id.encode('utf-8')))
#     except KeyboardInterrupt:
#         stop_server()
#
#
# def wait_player(player_index):  # NOT IN USE (I think)
#     conn, addr = network.sock.accept()
#     client_details = repr(conn.recv(1024))[2:-1]
#     print(currtime() + colored(
#         '[CONNECT] New connection from: ' + str(addr[0]) + ':' + str(addr[1]) + ' | ' + client_details, connect_color))
#     network.players += [['x', 'o'][player_index]]
#     conn.send(bytes(['x', 'o'][player_index].encode('utf-8')))
#
#
# def stop_room(room_id):
#     try:
#         print(currtime() + colored('[STOP-ROOM] Sending stop-code to the clients', exit_color))
#         network.players_online -= 2
#         send(room_id, 'server-stop')
#     except Exception as sending_stop_code_exception:
#         if debug:
#             print(format_exc())
#         print(currtime() + colored(
#             '[STOP-ROOM] Failed to send stop-code to the clients: ' + str(sending_stop_code_exception), exit_color))
#     delete_room(room_id)
#
#
# def stop_server():
#     print('\n' + currtime() + colored('[EXIT] Stopping server and closing socket...', exit_color))
#     try:
#         print(currtime() + colored('[EXIT] Sending stop-code to the clients', exit_color))
#         send('server-stop')
#     except Exception as sending_stop_code_exception:
#         print(
#             currtime() + colored('[EXIT] Failed to send stop-code to the clients: ' + str(sending_stop_code_exception),
#                                  exit_color))
#     network.sock.close()
#     for each in data.threads:
#         each.stop()
#     sys.exit()
#
#
# def update_table(room_id):
#     players_table = network.rooms[find_room_by_id(room_id)][2]
#     send(room_id, ';'.join([str(i) for i in players_table]))
#
#
# def start_room(room_id):
#     try:
#         print(currtime() + colored('[SESSION] Starting the game...', session_color))
#         sleep(0.5)
#         send(room_id, 'starting')
#         # let the client handle with it
#         sleep(0.5)
#         while True:
#             for i in range(2):
#                 client = network.rooms[find_room_by_id(room_id)][i]
#
#                 print(currtime() + colored(f'[SESSION] Player{i + 1}\'s move', session_color))
#                 try:
#                     client.send(b'your-move')
#                     # sleep, because client may pass it threw because of timings
#                     sleep(0.3)
#                     # update table for clients
#                     update_table(room_id)
#                 except BrokenPipeError:
#                     print(currtime() + colored(f'[SESSION] Player{i + 1} has disconnected', session_color))
#                     stop_room(room_id)
#
#                 data = repr(client.recv(1024).decode('utf-8'))[1:-1]
#                 try:
#                     network.players_table[int(data) - 1] = network.players[i]
#                     print(
#                         currtime() + colored(
#                             f'[SESSION] Received data from player{i + 1}: {data if data != "" else "<empty>"}',
#                             session_color))
#                 except:
#                     print(currtime() + colored(
#                         f'[ERROR] Received corrupted packet from player{i + 1}: {data if data != "" else "<empty>"}',
#                         err_color))
#                 update_table(room_id)
#                 checkwin(room_id)
#     # except KeyboardInterrupt:
#     #     stop_server()
#     except Exception as server_failure:
#         if debug:
#             print(format_exc())
#         print(currtime() + colored('[SERVER-STOP] Uncaught error:' + str(server_failure), err_color))
#         stop_room(room_id)
#
#
# def rooms_handler():
#     """
#     function, which will run rooms in threads
#     """
#     try:
#         while True:
#             for room in network.rooms:
#                 if room[4] == 'not-started':    # if room is not started
#                     Thread(target=start_room, args=(room[3],)).start()
#             sleep(0.2)
#     except KeyboardInterrupt:
#         stop_server()
#
#
# def init(ip='127.0.0.1', port=8083):
#     # this print is not colored, because info is always white
#     print(f'{currtime()}[INFO] Starting server on ip: {ip}; on port: {port}; server-version: {VERSION}')
#     try:
#         network.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         network.sock.bind((ip, port))
#         clients_listener = thread('Clients', target=connects_listener)
#         handle_rooms = thread('Rooms', target=rooms_handler)
#         data.threads = [clients_listener, handle_rooms]
#         clients_listener.start(), handle_rooms.start()
#     except KeyboardInterrupt:
#         stop_server()
#     except OSError:
#         print(currtime() + colored('[ERROR] Port already in use', err_color))
#
#
# init()
