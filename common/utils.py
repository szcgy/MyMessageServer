# -*- coding: utf8 -*-
from errors import PermissionDenied
from auth import validate_token


C_LENGTH = 4
L_LENGTH = 4
T_LENGTH = 32


def send(client, content):
    pass


def recv(client, content):
    cmd = unpack(client.recv(C_LENGTH))
    length = int(unpack(client.recv(C_LENGTH)))
    token = unpack(client.recv(T_LENGTH))

    if cmd != 0 and not validate_token(token):
        raise PermissionDenied

    content = unpack(client.recv(length))
    return content


def unpack(content):
    return bytes.decode(content)
