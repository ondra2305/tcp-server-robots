import socket
import threading
from config import *
from helpers import *


def calc_cl_key(cl_hash, kid):
    res = None
    if kid == 0:
        res = (cl_hash + C_KEY0) % 65536
    elif kid == 1:
        res = (cl_hash + C_KEY1) % 65536
    elif kid == 2:
        res = (cl_hash + C_KEY2) % 65536
    elif kid == 3:
        res = (cl_hash + C_KEY3) % 65536
    elif kid == 4:
        res = (cl_hash + C_KEY4) % 65536
    return res


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


        conn.settimeout(1)
        connected = True
        while connected:
            data = conn.recv(1024).decode(MSG_FORMAT)
            print(f"Message from [{addr}]: {data}")
            response = self.process_data(data, thread_id)
            conn.sendall(response.encode(MSG_FORMAT))
            if (response == SERVER_LOGIN_FAILED) or (response == SERVER_KEY_OUT_OF_RANGE_ERROR):
                break
            elif (response == SERVER_LOGIC_ERROR) or (response == SERVER_SYNTAX_ERROR):
                break
            elif (response == SERVER_OK):
                conn.sendall(SERVER_MOVE.encode(MSG_FORMAT))

        #conn.sendall(SERVER_LOGOUT.encode(MSG_FORMAT))
        conn.close()
        print(f"Client at {addr} disconnected.")

    def process_data(self, data, thread_id):
        messages = data.split('\a\b')
        response = SERVER_SYNTAX_ERROR

        state = self.connected_clients[thread_id]['con_state']
        username = self.connected_clients[thread_id]['username']

        if messages[1] != '':
            return response

        if state == 'connected':
            if len(messages) > 1 and not hasattr(self.process_data, 'username'):
                username = messages[0]
                print(f'{username} connected')
                response = SERVER_KEY_REQUEST
                self.connected_clients[thread_id]['username'] = username
                self.connected_clients[thread_id]['con_state'] = 'key_req'
            else:
                response = SERVER_SYNTAX_ERROR
        elif state == 'key_req':
            print(f'{username}: Recv {messages[0]} key')
            kid = int(messages[0])
            self.connected_clients[thread_id]['cl_hash'] = calc_client_hash(username)
            self.connected_clients[thread_id]['key_id'] = kid
            if kid > 4 or kid < 0:
                self.connected_clients[thread_id]['con_state'] = 'keyerr'
                response = SERVER_KEY_OUT_OF_RANGE_ERROR
            else:
                self.connected_clients[thread_id]['con_state'] = 'key_sent'
                res = calc_srv_key(self.connected_clients[thread_id]['cl_hash'], kid)
                response = f"{res}\a\b"
        elif state == 'key_sent':
            hashcalc = self.connected_clients[thread_id]['cl_hash']
            recvkey = int(messages[0])
            kid = self.connected_clients[thread_id]['key_id']
            print(f'Cl hash: _{hashcalc}_')
            print(f'Key recv: _{messages[0]}_')
            if calc_cl_key(hashcalc, kid) == recvkey:
                self.connected_clients[thread_id]['con_state'] = 'login_complete'
                response = SERVER_OK
            else:
                response = SERVER_LOGIN_FAILED
        elif state == 'login_complete':
            response = SERVER_MOVE
        else:
            response = SERVER_SYNTAX_ERROR

        return response

    def cl_auth(self, username, message):

        return
