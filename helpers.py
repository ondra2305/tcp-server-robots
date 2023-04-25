from config import *


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