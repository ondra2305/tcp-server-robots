import socket
import threading
import numpy as np

from config import *
from helpers import *
import uuid
import time

class Server:
    def __init__(self):
        self.connected_clients = {}

    def start_server(self, my_socket):
        print(f"Starting server on port {PORT}")
        my_socket.listen(1)
        print(f"Server is listening on: {SERVER}")
        while True:
            conn, addr = my_socket.accept()
            thread_id = str(uuid.uuid4())
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
        lock = threading.Lock()
        last_was_charging = False
        while connected:
            try:
                data = conn.recv(1024).decode(MSG_FORMAT)
                if not data:
                    break
                with lock:
                    message += data
                while "\a\b" in message:
                    message_parts = message.split("\a\b")
                    message = message_parts.pop()
                    print("Message parts:")
                    print(message_parts)
                    for part in message_parts:
                        print("Part:")
                        print(part)
                        with lock:
                            print(f"Last was charging? {last_was_charging}")
                            print(f"Message from [{addr}]: {part}\a\b, TI {thread_id}")
                            if last_was_charging and "FULL POWER" not in part:
                                raise SyntaxError("Did not recieve FULL POWER!")
                            last_was_charging = False
                            if "RECHARGING" in part:
                                conn.settimeout(5)
                                last_was_charging = True
                                part = part.replace("RECHARGING", "")
                            elif "FULL POWER" in part:
                                conn.settimeout(1)
                                part = part.replace("FULL POWER", "")
                            print("Part now:")
                            print(part)
                            if part == "":
                                continue
                            response = self.process_data(part + "\a\b", thread_id, robot)
                            conn.sendall(response.encode(MSG_FORMAT))
                            if response in [SERVER_LOGIN_FAILED, SERVER_KEY_OUT_OF_RANGE_ERROR, SERVER_LOGIC_ERROR,
                                            SERVER_SYNTAX_ERROR, SERVER_LOGOUT]:
                                connected = False
                                break
                            elif response == SERVER_OK:
                                conn.sendall(SERVER_MOVE.encode(MSG_FORMAT))
            except socket.timeout:
                print(f"Connection timed out for {addr}.")
                break
            except SyntaxError:
                conn.sendall(SERVER_LOGIC_ERROR.encode(MSG_FORMAT))
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
            if recvkey > 99999 or messages[0].endswith(" "):
                response = SERVER_SYNTAX_ERROR
            elif calc_cl_key(hashcalc, kid) == recvkey:
                self.connected_clients[thread_id]['con_state'] = 'move'
                response = SERVER_OK
            else:
                response = SERVER_LOGIN_FAILED
        elif state == 'move':
            print(f'Move: _{msg}_')
            if msg.endswith(" "):
                return SERVER_SYNTAX_ERROR
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
