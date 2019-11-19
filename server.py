# encoding: utf-8
import socket
import threading
import pickle


class ServerManager(object):
    def __init__(self, ipAddress, port, maxConnection, recvCallback):
        self.__bLoop = False
        self.ServerIp = ipAddress
        self.Port = port
        self.RecvData = recvCallback
        self.MaxConnection = maxConnection
        self.serverSocket = None
        self.clients = []
        self.BufferSize = 1024

    def Start(self):
        # 创建TCP套接字
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 创建UDP套接字
        # udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.serverSocket.bind((self.ServerIp, self.Port)) # 将地址绑定到套接字上
        self.serverSocket.listen(self.MaxConnection) # 设置并启动TCP监听器
        threading.Thread(target=self.__startThread).start()

    def Stop(self):
        self.__bLoop = False
        for client in self.clients:
            client.shutdown(2)
            client.close()

    def SendData(self, data):
        for client in self.clients:
            client.send(bytes(data, encoding='gb2312'))

    def __startThread(self):
        self.__bLoop = True
        while self.__bLoop:
            print("等待客户端连接")
            tcpClientSock, addr = self.serverSocket.accept() # 被动接收TCP客户端连接，一直等待直到连接到达（阻塞）
            print("上线客户端：", addr)
            self.clients.append(tcpClientSock)
            threading.Thread(target=self.__recvThread, args=(tcpClientSock,)).start()

    def __recvThread(self, client):
        while self.__bLoop:
            if not self.__bLoop:
                break
            data = client.recv(self.BufferSize) # 接收TCP消息
            # print(data)
            # 如果有数据加上时间戳后返回给客户端，因为只接受字节数据，所以把数据使用bytes函数转换
            if not data:
                self.clients.remove(client)
                print("下线客户端：", client.getpeername())
                break
            else:
                if self.RecvData:
                    self.RecvData(data)


if __name__ == "__main__":
    def recvdata(data):
        print(data)
server = ServerManager("192.168.1.246", 5200, 5, recvdata)
server.Start()

