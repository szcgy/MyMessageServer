# -*- coding: utf8 -*-
from errors import PermissionDenied
from auth import validate_token
import const


C_LENGTH = 4
L_LENGTH = 4
T_LENGTH = 32


def send(client, content):
    pass


def recv(client, content):
    cmd = int(client.recv(C_LENGTH), 16)
    length = int(client.recv(C_LENGTH), 16)
    token = unpack(client.recv(T_LENGTH))

    if cmd != const.LOGIN and not validate_token(token):
        raise PermissionDenied

    content = unpack(client.recv(length))
    return content


def unpack(content):
    return bytes.decode(content)
