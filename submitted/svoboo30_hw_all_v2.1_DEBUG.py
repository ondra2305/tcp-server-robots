import socket
import threading
import uuid
import random
import numpy as np

# SERVER MESSAGES
SERVER_MOVE = '102 MOVE\a\b'
SERVER_TURN_LEFT = '103 TURN LEFT\a\b'
SERVER_TURN_RIGHT = '104 TURN RIGHT\a\b'
SERVER_PICK_UP = '105 GET MESSAGE\a\b'
SERVER_LOGOUT = '106 LOGOUT\a\b'
SERVER_KEY_REQUEST = '107 KEY REQUEST\a\b'
SERVER_OK = '200 OK\a\b'
SERVER_LOGIN_FAILED = '300 LOGIN FAILED\a\b'
SERVER_SYNTAX_ERROR = '301 SYNTAX ERROR\a\b'
SERVER_LOGIC_ERROR = '302 LOGIC ERROR\a\b'
SERVER_KEY_OUT_OF_RANGE_ERROR = '303 KEY OUT OF RANGE\a\b'

S_KEY0 = 23019
S_KEY1 = 32037
S_KEY2 = 18789
S_KEY3 = 16443
S_KEY4 = 18189

C_KEY0 = 32037
C_KEY1 = 29295
C_KEY2 = 13603
C_KEY3 = 29533
C_KEY4 = 21952

S_KEYS = {0: S_KEY0, 1: S_KEY1, 2: S_KEY2, 3: S_KEY3, 4: S_KEY4}
C_KEYS = {0: C_KEY0, 1: C_KEY1, 2: C_KEY2, 3: C_KEY3, 4: C_KEY4}

PORT = 6969
SERVER = socket.gethostbyname(socket.gethostname())
SERVER_ADDR = (SERVER, PORT)
MSG_FORMAT = 'utf-8'

CLIENT_RECHARGING = 'RECHARGING\a\b'
CLIENT_FULL_POWER = 'FULL POWER\a\b'


def calc_client_hash(username):
    if len(username) > 20:
        return 0

    ascii_list = []
    ascii_total = 0
    for letter in username:
        ascii_value = ord(letter)
        ascii_list.append(ascii_value)
        ascii_total += ascii_value

    cl_hash = (ascii_total * 1000) % 65536
    print(f"clhash:{cl_hash}")
    return cl_hash


def calc_srv_key(cl_hash, kid):
    return (cl_hash + S_KEYS[kid]) % 65536


def calc_cl_key(cl_hash, kid):
    return (cl_hash + C_KEYS[kid]) % 65536


class Robot:
    def __init__(self):
        self.direction = None
        self.prev_x = None
        self.prev_y = None
        self.obstacle_dodging = False
        self.first_move = True
        self.dodging_moves = [SERVER_TURN_LEFT, SERVER_MOVE, SERVER_TURN_RIGHT, SERVER_MOVE, SERVER_MOVE,
                              SERVER_TURN_RIGHT, SERVER_MOVE]
        self.dodging_moves_R = [SERVER_TURN_RIGHT, SERVER_MOVE, SERVER_TURN_LEFT, SERVER_MOVE, SERVER_MOVE,
                                SERVER_TURN_LEFT, SERVER_MOVE]
        self.dodging_moves_L = [SERVER_TURN_LEFT, SERVER_MOVE, SERVER_TURN_RIGHT, SERVER_MOVE, SERVER_MOVE,
                                SERVER_TURN_RIGHT, SERVER_MOVE]
        self.wanted_direction = None
        self.obstacle_first = False
        self.second_move = False
        self.commands = []
        self.expected = ()

    def get_wanted_direction(self, x, y):
        target = max(abs(x), abs(y))

        if abs(x) == abs(y):
            if x < 0:
                return 'E'
            elif y < 0:
                return 'N'
            else:
                return self.direction
        elif target == abs(x):
            if x > 0:
                return 'W'
            elif x < 0:
                return 'E'
            elif x == 0:
                if y > 0:
                    return 'S'
                else:
                    return 'N'
        elif target == abs(y):
            if y > 0:
                return 'S'
            elif y < 0:
                return 'N'
            elif y == 0:
                if x > 0:
                    return 'W'
                else:
                    return 'E'

    def get_direction(self, x, y):
        if x > self.prev_x:
            return 'E'
        elif x < self.prev_x:
            return 'W'
        elif y > self.prev_y:
            return 'N'
        elif y < self.prev_y:
            return 'S'
        else:
            print("Prev is same, probably hit obstacle...")
            return self.direction

    def turn_to_target(self):
        if self.direction == 'W' and self.wanted_direction == 'S':
            self.direction = 'S'
            return SERVER_TURN_LEFT
        elif self.direction == 'W' and self.wanted_direction == 'N':
            self.direction = 'N'
            return SERVER_TURN_RIGHT

        elif self.direction == 'S' and self.wanted_direction == 'E':
            self.direction = 'E'
            return SERVER_TURN_LEFT
        elif self.direction == 'S' and self.wanted_direction == 'W':
            self.direction = 'W'
            return SERVER_TURN_RIGHT

        elif self.direction == 'N' and self.wanted_direction == 'E':
            self.direction = 'E'
            return SERVER_TURN_RIGHT
        elif self.direction == 'N' and self.wanted_direction == 'W':
            self.direction = 'W'
            return SERVER_TURN_LEFT

        elif self.direction == 'E' and self.wanted_direction == 'S':
            self.direction = 'S'
            return SERVER_TURN_RIGHT
        elif self.direction == 'E' and self.wanted_direction == 'N':
            self.direction = 'N'
            return SERVER_TURN_LEFT

        elif self.direction == 'W' and self.wanted_direction == 'E':
            print("Zasranej komouš")
            self.direction = 'N'
            return SERVER_TURN_RIGHT

        elif self.direction == 'E' and self.wanted_direction == 'W':
            self.direction = 'N'
            return SERVER_TURN_LEFT

        elif self.direction == 'N' and self.wanted_direction == 'S':
            self.direction = 'E'
            return SERVER_TURN_RIGHT

        elif self.direction == 'S' and self.wanted_direction == 'N':
            self.direction = 'W'
            return SERVER_TURN_RIGHT

        if self.direction == self.wanted_direction:
            return SERVER_MOVE

    def set_expected(self, x, y):
        if self.direction == "N":
            self.expected = (x, y + 1)
        elif self.direction == "S":
            self.expected = (x, y - 1)
        elif self.direction == "W":
            self.expected = (x - 1, y)
        elif self.direction == "E":
            self.expected = (x + 1, y)

    def move_to_0(self, x, y):
        y = y.split('\a\b')[0]

        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f'My new pos: {x},{y}')

        if "." in x:
            x_float = True
        else:
            x_float = False
        if "." in y:
            y_float = True
        else:
            y_float = False

        if x_float or y_float:
            return SERVER_SYNTAX_ERROR

        x = int(x)
        y = int(y)

        print("Expected:")
        print(self.expected)
        if len(self.commands) > 0:
            if self.commands[-1:] == [SERVER_MOVE] and not self.second_move:
                self.direction = self.get_direction(x, y)
                print(f"Direction: {self.get_direction(x, y)}")
                self.wanted_direction = self.get_wanted_direction(x, y)
                print(f"Wanted direction: {self.wanted_direction}")
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        if len(self.commands) > 0:
            print(self.commands)

        if self.first_move:
            if x == 0 and y == 0:
                self.commands.append(SERVER_PICK_UP)
                return SERVER_PICK_UP

            print(f"First move")
            self.first_move = False
            self.prev_x = x
            self.prev_y = y
            self.first_move = False
            self.second_move = True
            self.commands.append(SERVER_MOVE)
            self.commands.append(SERVER_MOVE)
            return SERVER_MOVE
        if self.second_move:
            if x == 0 and y == 0:
                self.commands.append(SERVER_PICK_UP)
                return SERVER_PICK_UP
            if self.prev_x == x and self.prev_y == y and (not self.obstacle_first):
                print(f"Second move")
                print("Hit obstacle on first move, going around")
                print("Cannot determine direction")
                self.obstacle_first = True
                self.second_move = True
                command = random.choice([SERVER_TURN_LEFT, SERVER_TURN_RIGHT])
                self.commands.append(command)
                return command
            elif self.obstacle_first:
                print(f"Second move p2")
                self.obstacle_first = False
                self.second_move = False
                self.prev_x = x
                self.prev_y = y
                self.commands.append(SERVER_MOVE)
                return SERVER_MOVE
            else:
                print(f"Second move")
                self.direction = self.get_direction(x, y)
                self.wanted_direction = self.get_wanted_direction(x, y)
                self.prev_x = x
                self.prev_y = y
                self.second_move = False
                self.commands.append(SERVER_MOVE)
                self.set_expected(x, y)
                return SERVER_MOVE

        if x == 0 and y == 0:
            self.commands.append(SERVER_PICK_UP)
            return SERVER_PICK_UP
        elif self.direction is not None and self.direction != self.wanted_direction \
                and self.commands[-1:] == [SERVER_MOVE] and not self.obstacle_dodging:
            print(f"DIRECTION IS NOT RIGHT, wanted {self.wanted_direction}, now {self.direction}")
            turn = self.turn_to_target()
            self.commands.append(turn)
            return turn
        elif self.direction is not None and self.direction != self.wanted_direction \
                and self.commands[-2:] == [SERVER_MOVE, SERVER_MOVE]:
            print(f"DIRECTION IS NOT RIGHT, wanted {self.wanted_direction}, now {self.direction}")
            if self.obstacle_dodging:
                print(f"Wanted dir changed during dodging...")
                self.obstacle_dodging = False
            turn = self.turn_to_target()
            self.commands.append(turn)
            return turn
        elif (x, y) != self.expected \
                and self.commands[-2:] == [SERVER_MOVE, SERVER_MOVE] and (not self.obstacle_dodging):
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(f"OBSTACLE HIT {self.expected}")
            if x == 0 and y == 1:
                self.dodging_moves = self.turn_to_target()
            elif x == 1 and y == 0:
                self.dodging_moves = self.turn_to_target()
            else:
                self.dodging_moves = [SERVER_TURN_LEFT, SERVER_MOVE, SERVER_TURN_RIGHT, SERVER_MOVE, SERVER_MOVE,
                                      SERVER_TURN_RIGHT, SERVER_MOVE]

            self.obstacle_dodging = True
            move = self.dodging_moves[0]
            print(f"Dodging, move now is {move}")
            self.dodging_moves.pop(0)
            self.prev_x = x
            self.prev_y = y
            self.commands.append(move)
            return move
        elif self.obstacle_dodging:
            if len(self.dodging_moves) <= 1:
                self.obstacle_dodging = False
                self.dodging_moves = [SERVER_TURN_LEFT, SERVER_MOVE, SERVER_TURN_RIGHT, SERVER_MOVE, SERVER_MOVE,
                                      SERVER_TURN_RIGHT, SERVER_MOVE]
                print("Dodging complete")
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                self.prev_x = x
                self.prev_y = y
                self.commands.append(SERVER_MOVE)
                self.set_expected(x, y)
                return SERVER_MOVE
            move = self.dodging_moves[0]
            print(f"Dodging, move now is {move}")
            self.dodging_moves = self.dodging_moves[1:]
            self.prev_x = x
            self.prev_y = y
            self.commands.append(move)
            return move
        else:
            print("Move forward:")
            print(f"{x}, {y}")
            self.prev_x = x
            self.prev_y = y
            self.set_expected(x, y)
            self.commands.append(SERVER_MOVE)
            return SERVER_MOVE


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
                    if "\a\b" not in data:
                        if self.connected_clients[thread_id]['con_state'] == 'connected':
                            if len(message) >= 19:
                                raise SyntaxError("Wrong username!")
                        elif self.connected_clients[thread_id]['con_state'] == 'move':
                            if len(message) >= 11:
                                raise SyntaxError("Confirmation too long!")
                        elif self.connected_clients[thread_id]['con_state'] == 'pickup':
                            if len(message) >= 99:
                                raise SyntaxError("Message too long!")
                    print("RECV MSG:")
                    print(message)
                while "\a\b" in message:
                    message_parts = message.split("\a\b")
                    message = message_parts.pop()
                    print(message_parts)
                    for part in message_parts:
                        print(part)
                        with lock:
                            print(f"Message from [{addr}]: {part}\a\b, TI {thread_id}")
                            if last_was_charging and "FULL POWER" not in part:
                                raise SystemError("Did not recieve FULL POWER!")
                            last_was_charging = False
                            if "RECHARGING" in part:
                                conn.settimeout(5)
                                last_was_charging = True
                                part = part.replace("RECHARGING", "")
                            elif "FULL POWER" in part:
                                conn.settimeout(1)
                                part = part.replace("FULL POWER", "")
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
            except SystemError:
                conn.sendall(SERVER_LOGIC_ERROR.encode(MSG_FORMAT))
                break
            except SyntaxError:
                conn.sendall(SERVER_SYNTAX_ERROR.encode(MSG_FORMAT))
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


def main():
    my_server = Server()
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    my_socket.bind(SERVER_ADDR)
    my_server.start_server(my_socket)


if __name__ == "__main__":
    main()
