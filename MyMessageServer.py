import sys
import os
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

import threading
import time
import socket

from common.auth import validate_password
from common.utils import send, recv
from common.models import Session
from common import const

#我不是QQ
class MyMessageServer:
    serverSocket = socket.socket()  #服务用Socket
    isOpen = False                  #服务启动标志
    accepting = False               #正在接受客户端标志
    clientsList = {}                #在线客户列表
    blackIpList = {}                #黑名单IP

    def __init__(self):
        #设定好侦听端口
        self.serverSocket.bind(("0.0.0.0",9099))

    #开启socket
    def openServer(self):
        if self.isOpen:
            return True
        try:
            #开始侦听
            self.serverSocket.listen()
            self.isOpen = True
            return True
        except ConnectionRefusedError as ex:
            #侦听都出错那我就没办法了
            print(ex.strerror)
            self.isOpen = False
            return False

    #客户端接受消息线程主体
    def resciveThread(self,client,ClientKey):
        #在服务开启期间一直运行
        while self.isOpen:
            try:
                #接受数据
                cmd, token, data = recv(client)
                if cmd == const.MSG and len(data) > 0:
                    #有数据

                    #打印出来看
                    #print("\"{0}\" :{1}".format(ClientKey,bytes.decode(data)))

                    #传给所有客户端
                    for _clientIp,_client in self.clientsList.items():
                        send(_client, (const.MSG, '0'*32, data))
                else:
                    #没数据，估计是网络有问题，断掉
                    #客户端不能发空消息不然也会断掉
                    client.close()
                    del self.clientsList[ClientKey]

                    break
            except (ConnectionAbortedError, ConnectionResetError):
                #客户端主动把连接中断了
                if self.accepting:
                    del self.clientsList[ClientKey]
                break
  
    def disconnect(self, client, key):
        try:
            client.close()
        except:
            pass
        del self.clientsList[key]

    def login(self, client, key):
        try:
            cmd, token, content = recv(client)
        except (ConnectionAbortedError, ConnectionResetError):
            return False
        if cmd != const.LOGIN:
            return False

        def extract():
            args = content.split('\t')
            if len(args) < 2:
                return None
            return args

        args = extract()
        if not args:
            return False

        username, password = args[0], args[1]
        user = validate_password(username, password)
        if not user:
            return None
        session = Session.setSession(user)
        return session


    #接受客户端线程主体
    def acceptingThread(self):
        while self.accepting:
            try:
                #一直等待新的客户端
                newClient,newOne = self.serverSocket.accept()
                #等到了
                #看在不在黑名单里

                if newOne[0] in self.blackIpList:

                    #在黑名单里
                    if self.blackIpList[newOne[0]] >= 3:
                        #还失败了三次
                        newClient.close()

                        #看看是谁
                        #print("refuse {0} connect".format(newOne[0]))

                        #继续等
                        continue
                #看看客户端是不是用51000来连的
                if(False):
                    #不是断掉
                    newClient.close()

                    #记在小本本里
                    if(self.blackIpList.__contains__(newOne[0])):
                        self.blackIpList[newOne[0]] += 1
                    else:
                        self.blackIpList[newOne[0]] = 1
                else:
                    #IP+端口号产生一个键
                    newkey = "{0}:{1}".format(newOne[0],newOne[1])

                    #添加一个客户键值对
                    self.clientsList[newkey] = newClient

                    session = self.login(newClient, newkey)
                    if session:
                        #开启这个客户的读取消息线程
                        send(newClient, (const.LOGIN, '0'*32, session.token))
                        threading.Thread(target=self.resciveThread,args=(newClient,newkey)).start()
                    else:
                        self.disconnect(newClient, newkey)
            except OSError:
                break

    #开始接受客户端
    def startAccept(self):
        #开始接受客户端
        self.accepting = True
        #可以侦听的
        if self.openServer():
            #开启侦听线程
            threading.Thread(target=self.acceptingThread).start()

    #停止接受客户端
    def stopAccept(self):
        #还是会等最后一个进来
        self.accepting = False

    #关闭服务
    def closeServer(self):
        #关掉所有循环的标记
        self.isOpen = False
        self.accepting = False
        #断开全部客户端
        for clientIp,client in self.clientsList.items():
            client.close()
            print("{0} disconnected!" % clientIp)
        #侦听也断掉
        self.serverSocket.close()
        print("Program Closed!")

#主函数，运行之后开启端口 指令 -a 开始接受客户端 -s 停止接受客户端 -x 停止服务       
def myMessageServerMain():
    server = MyMessageServer()
    if server.openServer():
        command = input("command:")
        while command != "-x":
            if command == "-a":
                server.startAccept()
            if command == "-s":
                server.stopAccept()
            command = input("command:")
        server.closeServer()

if __name__ == "__main__":
    myMessageServerMain()
