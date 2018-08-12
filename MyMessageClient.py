import socket
import threading
import time
from common import const
from common import utils
import tkinter as tk

class MyMessageClient():
    
    clientSocket = socket.socket()
    isOpen = False
    user = ""
    password = ""
    token = "00000000000000000000000000000000"#32个0
    guiRoot = tk.Tk()
    __talkArea = tk.Text(guiRoot)
    __typeArea = tk.Text(guiRoot,height=5)

    def __init__(self,userName = "anonymous",passWord = "Failed"):
        sendButton = tk.Button(self.guiRoot,text="发送",command=self.sendMsg)
        self.user = userName
        self.password = passWord
        self.__talkArea.pack(fill=tk.BOTH)
        self.__typeArea.pack(side=tk.LEFT,fill = tk.X)
        sendButton.pack(side=tk.RIGHT)
        
    def connectServer(self):
        try:
            self.clientSocket.connect(("119.23.26.133",9099))
            utils.send(self.clientSocket,(const.LOGIN,self.token,'{0}\t{1}'.format(self.user,self.password)))
            try:
                cmdType,token,data = utils.recv(self.clientSocket,False)
                if cmdType == const.LOGIN:
                    self.token = data
                    #print("recive token %s"%data)
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
                        self.__talkArea.insert(tk.END,("%s\n"%data))
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
        msg = self.__typeArea.dump('1.0',tk.END)
        if msg[0][0] == 'text' and len(msg[0][1]) > 0:
            self.__typeArea.delete('1.0',tk.END)
            utils.send(self.clientSocket,(const.MSG,self.token,'{0}:\t{1}'.format(self.user,msg[0][1])))

def main():
    
    start = MyMessageClient(input("User Name:"),input("Password:"))
    #start.guiRoot.mainloop()
    if(start.connectServer()):
        start.startReading()
        print("Loggin Successed!")
        start.guiRoot.mainloop()
        start.disconnect()
        time.sleep(1)
        print("Program Closed!")
    else:
        print("Loggin Failed!")

if __name__ == "__main__":
    main()