from config import *
import random


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
                and self.commands[-1:] == [SERVER_MOVE]:
            print(f"Direction is not right, wanted {self.wanted_direction}, now {self.direction}")
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
