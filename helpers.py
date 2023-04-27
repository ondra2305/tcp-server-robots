from config import *
import math

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
    res = None
    if kid == 0:
        res = (cl_hash + S_KEY0) % 65536
    elif kid == 1:
        res = (cl_hash + S_KEY1) % 65536
    elif kid == 2:
        res = (cl_hash + S_KEY2) % 65536
    elif kid == 3:
        res = (cl_hash + S_KEY3) % 65536
    elif kid == 4:
        res = (cl_hash + S_KEY4) % 65536
    return res


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


class Robot:
    def __init__(self):
        self.direction = None
        self.xPos = None
        self.yPos = None
        self.first_move = True

    def move_to_0(self, x, y):
        y = y.split('\a\b')[0]
        print(f'My pos: {x},{y}')

        self.xPos = int(x)
        self.yPos = int(y)

        distance = math.sqrt(self.xPos**2 + self.yPos**2)

        if distance == 0:
            return SERVER_PICK_UP

        if self.first_move:
            self.first_move = False
            return SERVER_MOVE

        if self.direction is None:
            if self.xPos > 0:
                self.direction = 'W'
            elif self.xPos < 0:
                self.direction = 'E'
            elif self.yPos > 0:
                self.direction = 'S'
            elif self.yPos < 0:
                self.direction = 'N'

        if self.direction == 'E':
            if self.xPos > 0:
                return SERVER_MOVE
            elif self.yPos < 0:
                self.direction = 'N'
                return SERVER_TURN_LEFT
            else:
                self.direction = 'S'
                return SERVER_TURN_RIGHT

        elif self.direction == 'W':
            if self.xPos < 0:
                return SERVER_MOVE
            elif self.yPos > 0:
                self.direction = 'S'
                return SERVER_TURN_LEFT
            else:
                self.direction = 'N'
                return SERVER_TURN_RIGHT

        elif self.direction == 'N':
            if self.yPos > 0:
                return SERVER_MOVE
            elif self.xPos > 0:
                self.direction = 'W'
                return SERVER_TURN_LEFT
            else:
                self.direction = 'E'
                return SERVER_TURN_RIGHT

        elif self.direction == 'S':
            if self.yPos < 0:
                return SERVER_MOVE
            elif self.xPos < 0:
                self.direction = 'E'
                return SERVER_TURN_LEFT
            else:
                self.direction = 'W'
                return SERVER_TURN_RIGHT

        return SERVER_MOVE
