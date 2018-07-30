import socket
import threading
import time
from common import const
from common import utils
class MyMessageClient():
    clientSocket = socket.socket()
    isOpen = False
    user = ""
    password = ""
    token = ""
    def __init__(self,userName = "anonymous",passWord = "Failed"):
        self.user = userName
        self.password = passWord

    def connectServer(self):
        try:
            self.clientSocket.connect(("119.23.26.133",9099))
            utils.send(self.clientSocket,(const.LOGIN,self.token,'{0}\t{1}'.format(self.user,self.password)))
            try:
                cmdType,token,data = utils.recv(self.clientSocket,False)
                if cmdType == const.LOGIN:
                    self.token = data
                    print("recive token %s"%data)
                    self.isOpen = True
                    return True
                else:
                    return False
            except:
                return False
        except ConnectionRefusedError as ex:
            print(ex.strerror)
            self.isOpen = False
            return False
            
    def disconnect(self):
        utils.send(self.clientSocket,(const.LOGOUT,self.token,""))
        

    def readingThread(self):
        while self.isOpen:
            try:
                cmdType,token,data = utils.recv(self.clientSocket,False)
                if cmdType == const.MSG:
                    if len(data)>0:
                        print(data)
                elif cmdType == const.LOGOUT:
                    print("退出登录")
                    self.isOpen = False
                    self.clientSocket.close()
                    break                                        
            except (ConnectionAbortedError,ConnectionResetError):
                print("服务器断开连接！")
                self.isOpen = False
                break
    def startReading(self):
        threading.Thread(target=self.readingThread).start()
    def sendMsg(self,msg="None"):
        utils.send(self.clientSocket,(const.MSG,self.token,'{0}:\t{1}'.format(self.user,msg)))

def main():
    start = MyMessageClient(input("User Name:"),input("Password:"))
    if(start.connectServer()):
        start.startReading()
        print("Loggin Successed!")
        while start.isOpen:
            data = input()
            if data == "-x":
                start.disconnect()
                time.sleep(1)
                break
            start.sendMsg(data)
    else:
        print("Loggin Failed!")

if __name__ == "__main__":
    main()