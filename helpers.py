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
                              SERVER_TURN_RIGHT, SERVER_MOVE, SERVER_TURN_LEFT]
        self.wanted_direction = None
        self.corrected = False
        self.turning_around = False
        self.obstacle_first = False
        self.second_move = True
        self.commands = []

    def get_wanted_direction(self, x, y):
        target = max(abs(x), abs(y))

        if abs(x) == abs(y):
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

        elif self.direction == 'W' and self.wanted_direction == 'E' and not self.turning_around:
            print("Zasranej komouš")
            self.direction = 'N'
            self.turning_around = True
            return SERVER_TURN_RIGHT
        elif self.direction == 'W' and self.wanted_direction == 'E' and self.turning_around:
            print("Zasranej komouš")
            self.direction = 'E'
            self.turning_around = False
            return SERVER_TURN_RIGHT

        elif self.direction == 'E' and self.wanted_direction == 'W' and not self.turning_around:
            self.direction = 'N'
            self.turning_around = True
            return SERVER_TURN_LEFT
        elif self.direction == 'E' and self.wanted_direction == 'W' and self.turning_around:
            self.direction = 'E'
            self.turning_around = False
            return SERVER_TURN_LEFT

        elif self.direction == 'N' and self.wanted_direction == 'S' and not self.turning_around:
            self.direction = 'E'
            self.turning_around = True
            return SERVER_TURN_RIGHT
        elif self.direction == 'N' and self.wanted_direction == 'S' and self.turning_around:
            self.direction = 'S'
            self.turning_around = False
            return SERVER_TURN_RIGHT

        elif self.direction == 'S' and self.wanted_direction == 'N' and not self.turning_around:
            self.direction = 'E'
            self.turning_around = True
            return SERVER_TURN_RIGHT
        elif self.direction == 'S' and self.wanted_direction == 'N' and self.turning_around:
            self.direction = 'N'
            self.turning_around = False
            return SERVER_TURN_RIGHT

    def move_to_0(self, x, y):
        # DO NOT EDIT
        y = y.split('\a\b')[0]
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f'My new pos: {x},{y}')
        x = int(x)
        y = int(y)
        if (not self.obstacle_dodging) and (len(self.commands) > 0):
            if self.commands[-1:] == [SERVER_MOVE]:
                self.direction = self.get_direction(x, y)
                print(f"Direction: {self.get_direction(x, y)}")

        self.wanted_direction = self.get_wanted_direction(x, y)
        print(f"Wanted direction: {self.wanted_direction}")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

        if len(self.commands) > 0:
            print(self.commands)

        if self.first_move or self.second_move:
            if x == 0 and y == 0:
                self.commands.append(SERVER_PICK_UP)
                return SERVER_PICK_UP
            if self.first_move:
                print(f"First move")
                self.first_move = False
                self.prev_x = x
                self.prev_y = y
                self.first_move = False
                self.commands.append(SERVER_MOVE)
                return SERVER_MOVE
            elif self.prev_x == x and self.prev_y == y and not self.obstacle_first:
                print(f"Second move")
                print("Hit obstacle on first move, going around")
                print("Cannot determine direction")
                self.obstacle_first = True
                self.commands.append(SERVER_TURN_LEFT)
                return SERVER_TURN_LEFT
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
                return SERVER_MOVE

        if x == 0 and y == 0:
            self.commands.append(SERVER_PICK_UP)
            return SERVER_PICK_UP
        elif self.direction is not None and self.direction != self.wanted_direction:
            print(f"Direction is not right, wanted {self.wanted_direction}, now {self.direction}")
            turn = self.turn_to_target()
            self.commands.append(turn)
            return turn
        elif self.prev_x == x and self.prev_y == y and (not self.obstacle_dodging) \
                and self.commands[-1:] == [SERVER_MOVE]:
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(f"OBSTACLE HIT {x} {y}")
            self.obstacle_dodging = True
            move = self.dodging_moves[0]
            print(f"Dodging, move now is {move}")
            self.dodging_moves = self.dodging_moves[1:]
            self.prev_x = x
            self.prev_y = y
            self.commands.append(move)
            return move
        elif self.obstacle_dodging:
            if len(self.dodging_moves) == 1:
                self.obstacle_dodging = False
                self.dodging_moves = [SERVER_TURN_LEFT, SERVER_MOVE, SERVER_TURN_RIGHT, SERVER_MOVE, SERVER_MOVE,
                                      SERVER_TURN_RIGHT, SERVER_MOVE, SERVER_TURN_LEFT]
                print("Dodging complete")
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                self.prev_x = x
                self.prev_y = y
                self.commands.append(SERVER_TURN_LEFT)
                return SERVER_TURN_LEFT
            move = self.dodging_moves[0]
            print(f"Dodging, move now is {move}")
            self.dodging_moves = self.dodging_moves[1:]
            self.prev_x = x
            self.prev_y = y
            return move
        else:
            print("Move forward:")
            print(f"{x}, {y}")
            self.prev_x = x
            self.prev_y = y
            self.commands.append(SERVER_MOVE)
            return SERVER_MOVE
