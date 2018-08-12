# -*- coding: utf8 -*-
from common.errors import PermissionDenied
from common.auth import validate_token
from common import const
import base64


C_LENGTH = 4
L_LENGTH = 4
T_LENGTH = 32


def send(client, content):
    cmdType,token,cmd = content
    if not isinstance(cmd, (bytes, )):
        cmd = cmd.encode('utf8')
    length = len(cmd)
    if length < 65536 and len(token)==32:
        data = ("%04x%04x%s" % (cmdType,length,token)).encode('utf8')
        data += cmd
        try:
            client.send(data)
            return True
        except:
            return False
    print("Command Too Long!!!")
    return False

def recv(client,isServer = True):
    tryRecv = client.recv(C_LENGTH)
    if len(tryRecv) == C_LENGTH:
        cmd = int(tryRecv, 16)
        length = int(client.recv(C_LENGTH), 16)
        token = unpack(client.recv(T_LENGTH))
        if isServer:
            if cmd != const.LOGIN and not validate_token(token):
                raise PermissionDenied
        if length>0:
            content = unpack(client.recv(length))
        else:
            content = ""
        return cmd, token, content
    else:
        raise ConnectionAbortedError


def unpack(content):
    print([content, ])
    return bytes.decode(content)

