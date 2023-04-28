from config import *
import math
import random
from collections import deque


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
        self.prev_x = None
        self.prev_y = None
        self.obstacle_dodging = False
        self.first_move = True
        self.dodging_moves = [SERVER_TURN_LEFT, SERVER_MOVE, SERVER_TURN_RIGHT, SERVER_MOVE, SERVER_MOVE,
                              SERVER_TURN_RIGHT, SERVER_MOVE]
        self.wanted_direction = None
        self.corrected = False

    def get_wanted_direction(self, x, y):
        bigger = max(abs(x), abs(y))

        if bigger == abs(x):
            if x > 0:
                return 'W'
            elif x < 0:
                return 'E'
            elif x == 0:
                if y > 0:
                    return 'S'
                else:
                    return 'N'
        elif bigger == abs(y):
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

    def move_to_0(self, x, y):
        # DO NOT EDIT
        y = y.split('\a\b')[0]
        print(f'My new pos: {x},{y}')
        print(f'Direction: {self.direction}')
        x = int(x)
        y = int(y)
        if self.direction is not None:
            print(f"Direction based on previous: {self.get_direction(x, y)}")


        if self.first_move:
            print(f"First move - p1")
            self.prev_x = x
            self.prev_y = y
            self.first_move = False
            return SERVER_MOVE
        elif self.direction is None and not self.obstacle_dodging:
            print(f"First move - p2")

            self.direction = self.get_direction(x, y)
            self.wanted_direction = self.get_wanted_direction(x, y)
            if self.direction == self.wanted_direction:
                self.wanted_direction = None
            self.prev_x = x
            self.prev_y = y


            print(f"Direction set to: {self.direction}")
            print(f"Wanted direction: {self.wanted_direction}")

        if x == 0 and y == 0:
            return SERVER_PICK_UP
        elif self.prev_x == x and self.prev_y == y and not self.obstacle_dodging:
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(f"OBSTACLE HIT {x} {y}")
            self.obstacle_dodging = True
            move = self.dodging_moves[0]
            print(f"Dodging, move now is {move}")
            self.dodging_moves = self.dodging_moves[1:]
            self.prev_x = x
            self.prev_y = y
            return move
        elif self.obstacle_dodging:
            if len(self.dodging_moves) == 0:
                self.obstacle_dodging = False
                self.dodging_moves = [SERVER_TURN_LEFT, SERVER_MOVE, SERVER_TURN_RIGHT, SERVER_MOVE, SERVER_MOVE,
                                      SERVER_TURN_RIGHT, SERVER_MOVE]
                print("Dodging complete, moving forward")
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


                #if self.direction is None:
                #    self.direction = self.get_direction(x, y)
                #    print(f"Direction now {self.direction}")

                self.prev_x = x
                self.prev_y = y
                return SERVER_MOVE
            move = self.dodging_moves[0]
            print(f"Dodging, move now is {move}")
            self.dodging_moves = self.dodging_moves[1:]
            self.prev_x = x
            self.prev_y = y
            return move
        elif self.direction != self.wanted_direction:
            print(f"Direction is not right, wanted {self.wanted_direction}, now {self.direction}")
            if self.direction == 'W' and self.wanted_direction == 'S':
                self.direction = 'S'
                return SERVER_TURN_LEFT
            if self.direction == 'S' and self.wanted_direction == 'E':
                self.direction = 'E'
                return SERVER_TURN_RIGHT
            if self.direction == 'N' and self.wanted_direction == 'E':
                self.direction = 'E'
                return SERVER_TURN_RIGHT
            if self.direction == 'N' and self.wanted_direction == 'W':
                self.direction = 'W'
                return SERVER_TURN_LEFT
            if self.direction == 'E' and self.wanted_direction == 'S':
                self.direction = 'S'
                return SERVER_TURN_RIGHT
            else:
                print(f"Direction is not right, wanted {self.wanted_direction}, now {self.direction}")
        else:
            print("Move forward:")
            if x == 0 or y == 0 and not self.corrected:
                print("Hit 0 on one of the axis")
                self.wanted_direction = self.get_wanted_direction(x, y)
                self.corrected = True
            self.prev_x = x
            self.prev_y = y
            return SERVER_MOVE
