# -*- coding: utf8 -*-
from errors import PermissionDenied
from auth import validate_token
import const


C_LENGTH = 4
L_LENGTH = 4
T_LENGTH = 32


def send(client, content):
    cmdType,token,cmd = content
    length = len(cmd)
    if length < 65536:
        data = "%04x%04x%032X" % cmdType,length,token
        data += cmd
        try:
            client.send(data.encode())
            return True
        except:
            return False
    print("Command Too Long!!!")
    return False

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
