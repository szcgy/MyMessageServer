# -*- coding: utf8 -*-
from common.errors import PermissionDenied
from common.auth import validate_token
from common import const


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

def recv(client,isServer = True):
    cmd = int(client.recv(C_LENGTH), 16)
    length = int(client.recv(C_LENGTH), 16)
    token = unpack(client.recv(T_LENGTH))
    if isServer:
        if cmd != const.LOGIN and not validate_token(token):
            raise PermissionDenied
    if length>0:
        content = (cmd,unpack(client.recv(length)))
    else:
        content = (cmd,"")
    return cmd, token, content


def unpack(content):
    return bytes.decode(content)
