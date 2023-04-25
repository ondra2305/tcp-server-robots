import socket

from config import *

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(SERVER_ADDR)


def send(msg):
    message = msg.encode(MSG_FORMAT)
    client.send(message)


def receive():
    received_shit = False

    while True:
        data = client.recv(1024).decode(MSG_FORMAT)
        print(f"Received a message from server: {data}")
        if data == SERVER_KEY_REQUEST:
            send('32037\a\b')
        if data == SERVER_LOGOUT or data == SERVER_OK:
            print('Received logout, ending...')
            break
        if data == '63803\a\b':
            send('63803\a\b')
        else:
            if not received_shit:
                received_shit = True
            else:
                print('Timeout')
                break
            continue
    client.close()


send('Mnau!\a\b')
receive()
