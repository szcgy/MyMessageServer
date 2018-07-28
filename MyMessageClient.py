import socket
import threading
import time

class MyMessageClient():
    clientSocket = socket.socket()
    isOpen = False
    user = ""
    password = ""
    token = 0
    def __init__(self,userName = "anonymous",passWord = "Failed"):
        self.user = userName
        self.password = passWord
    def __sendCmd(self,cmdType,cmd):
        length = len(cmd)
        if length < 65536:
            data = "%04x%04x%032X" % cmdType,length,self.token
            data += cmd
            try:
                self.clientSocket.send(data.encode())
                return True
            except:
                return False
        print("Command Too Long!!!")
        return False
    def connectServer(self):
        try:
            self.clientSocket.connect(("119.23.26.133",9099))
            self.clientSocket.send('-u {0} -p {1}'.format(self.user,self.password).encode())
            self.isOpen = True
            return True
        except ConnectionRefusedError as ex:
            print(ex.strerror)
            self.isOpen = False
            return False
    def disconnect(self):
        self.isOpen = False
        self.clientSocket.close()
    def readingThread(self):
        while self.isOpen:
            try:
                data = bytes.decode(self.clientSocket.recv(255))
                if len(data)>0:
                    print(data)
            except (ConnectionAbortedError,ConnectionResetError):
                self.isOpen = False
                break
    def startReading(self):
        threading.Thread(target=self.readingThread).start()
    def sendMsg(self,msg="None"):
        self.clientSocket.send(('\"{0}\":{1}'.format(self.user,msg).encode()))

def main():
    start = MyMessageClient(input("User Name:"),input("Password:"))
    if(start.connectServer()):
        start.startReading()
        print("Loggin Successed!")
        while start.isOpen:
            data = input()
            if data == "-x":
                break
            start.sendMsg(data)
        start.disconnect()
    else:
        print("Loggin Failed!")

if __name__ == "__main__":
    main()