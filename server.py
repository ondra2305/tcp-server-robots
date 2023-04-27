import socket
import threading
import numpy as np

from config import *
from helpers import *


class Server:
    def __init__(self):
        self.connected_clients = {}

    def start_server(self, my_socket):
        print(f"Starting server on port {PORT}")
        my_socket.listen(1)
        print(f"Server is listening on: {SERVER}")
        while True:
            conn, addr = my_socket.accept()
            thread_id = threading.get_ident()
            thread = threading.Thread(target=self.handle_cl_conn, args=(conn, addr, thread_id))
            self.connected_clients[thread_id] = {
                'con_state': 'connected',
                'conn': conn,
                'addr': addr,
                'username': None,
                'key_id': None,
                'cl_hash': None
            }
            thread.start()

    def handle_cl_conn(self, conn, addr, thread_id):
        print(f"New connection from: {addr}.")
        robot = Robot()

        conn.settimeout(1)
        connected = True
        message = ""
        while connected:
            try:
                data = conn.recv(1024).decode(MSG_FORMAT)
                if not data:
                    break
                message += data
                if message.endswith('\a\b'):
                    #message = message[:-2]
                    print(f"Message from [{addr}]: {message}")
                    response = self.process_data(message, thread_id, robot)
                    conn.sendall(response.encode(MSG_FORMAT))
                    if response in [SERVER_LOGIN_FAILED, SERVER_KEY_OUT_OF_RANGE_ERROR, SERVER_LOGIC_ERROR,
                                    SERVER_SYNTAX_ERROR, SERVER_LOGOUT]:
                        connected = False
                        break
                    elif response == SERVER_OK:
                        conn.sendall(SERVER_MOVE.encode(MSG_FORMAT))
                    message = ""
            except socket.timeout:
                print(f"Connection timed out for {addr}.")
                break

        conn.close()
        print(f"Client at {addr} disconnected.")

    def process_data(self, data, thread_id, robot):
        messages = data.split('\a\b')
        response = SERVER_SYNTAX_ERROR

        state = self.connected_clients[thread_id]['con_state']
        username = self.connected_clients[thread_id]['username']

        message_count = len(messages)
        msg = messages[0]
        if message_count > 1 and messages[1] != '':
            return response

        if state == 'connected':
            username = messages[0]

            if len(messages) > 1 and not hasattr(self.process_data, 'username') and len(username) <= 18:
                print(f'{username} connected')
                response = SERVER_KEY_REQUEST
                self.connected_clients[thread_id]['username'] = username
                self.connected_clients[thread_id]['con_state'] = 'key_req'
            else:
                response = SERVER_SYNTAX_ERROR
        elif state == 'key_req':
            print(f'{username}: Recv {messages[0]} key')
            if not np.char.isnumeric(messages[0]):
                self.connected_clients[thread_id]['con_state'] = 'keyerr'
                response = SERVER_SYNTAX_ERROR
            else:
                kid = int(messages[0])
                print(f'KID: {kid}')
                self.connected_clients[thread_id]['cl_hash'] = calc_client_hash(username)
                self.connected_clients[thread_id]['key_id'] = kid
                if 4 >= kid >= 0:
                    self.connected_clients[thread_id]['con_state'] = 'key_sent'
                    res = calc_srv_key(self.connected_clients[thread_id]['cl_hash'], kid)
                    response = f"{res}\a\b"
                else:
                    self.connected_clients[thread_id]['con_state'] = 'keyerr'
                    response = SERVER_KEY_OUT_OF_RANGE_ERROR
        elif state == 'key_sent':
            hashcalc = self.connected_clients[thread_id]['cl_hash']
            recvkey = int(messages[0])
            kid = self.connected_clients[thread_id]['key_id']
            print(f'Cl hash: _{hashcalc}_')
            print(f'Key recv: _{messages[0]}_')
            if recvkey > 99999:
                response = SERVER_SYNTAX_ERROR
            elif calc_cl_key(hashcalc, kid) == recvkey:
                self.connected_clients[thread_id]['con_state'] = 'move'
                response = SERVER_OK
            else:
                response = SERVER_LOGIN_FAILED
        elif state == 'move':
            print(f'Move: {msg}')
            msg = data.split(' ')
            response = robot.move_to_0(msg[1], msg[2])
            if response == SERVER_PICK_UP:
                self.connected_clients[thread_id]['con_state'] = 'pickup'
        elif state == 'pickup':
            print(f'Tajny vzkaz: {msg}')
            response = SERVER_LOGOUT
        else:
            response = SERVER_SYNTAX_ERROR

        return response

    def cl_auth(self, username, message):

        return
