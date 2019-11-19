# encoding: utf-8
import socket
import select
import threading

# 设置发送缓冲域大小
SEND_BUF_SIZE = 102400
# 设置接收缓冲域大小
RECV_BUF_SIZE = 102400

class ServerManager(object):
    def __init__(self, server_addr, MaxConnections=10, recvCallback=None, conncountCallback=None):
        self.__bLoop = True
        self.online_count = 0
        self.recvCallback = recvCallback
        self.conncountCallback = conncountCallback
        self.sSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.sSocket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SEND_BUF_SIZE)
        self.sSocket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, RECV_BUF_SIZE)
        self.sSocket.bind(server_addr)
        self.sSocket.listen(MaxConnections)
        self.epoll = select.epoll()
        self.epoll.register(self.sSocket.fileno(), select.EPOLLIN | select.EPOLLET)
        self.cSocketDict = {self.sSocket.fileno(): self.sSocket}
        self.cInfoDict = {}
        threading.Thread(target=self.__start_server).start()

    def __start_server(self):
        while self.__bLoop:
            events = self.epoll.poll()
            # print("当前存在%d个事件"%(len(events)))
            for fd, event in events:
                rsocket = self.cSocketDict[fd]
                if rsocket == self.sSocket:
                    csocket, cinfo = self.sSocket.accept()
                    print("新的客户端连接[%s]" % (str(cinfo)))
                    self.online_count = self.online_count+1
                    if self.conncountCallback:
                        self.conncountCallback(self.online_count)
                    self.cSocketDict[csocket.fileno()] = csocket
                    self.cInfoDict[csocket.fileno()] = cinfo
                    self.epoll.register(csocket.fileno(), select.EPOLLIN | select.EPOLLET)

                # 可读事件
                elif event & select.EPOLLIN:
                    try:
                        recvData = rsocket.recv(RECV_BUF_SIZE)
                    except ConnectionResetError:
                        print("客户端[%s]强制关闭了一个现有的连接" % (str(self.cInfoDict[fd])))
                        self.epoll.modify(fd, select.EPOLLHUP)
                    else:
                        if recvData:
                            # print("客户端[%s],收到数据:[%s]" % ((rsocket.getpeername()), recvData.decode("utf-8")))
                            if self.recvCallback:
                                self.recvCallback(recvData)
                            self.epoll.modify(fd, select.EPOLLOUT)
                        else:
                            print("客户端[%s]退出" % (str(self.cInfoDict[fd])))
                            self.online_count = self.online_count-1
                            if self.conncountCallback:
                                self.conncountCallback(self.online_count)
                            self.epoll.unregister(fd)
                            rsocket.close()
                            del self.cSocketDict[fd]
                # 可写事件
                elif event & select.EPOLLOUT:
                    # rsocket.send("server recv data".encode("utf-8"))
                    self.epoll.modify(fd, select.EPOLLIN)

                # 关闭事件
                elif event & select.EPOLLHUP:
                    print("客户端[%s]退出" % (str(self.cInfoDict[fd])))
                    self.online_count = self.online_count - 1
                    if self.conncountCallback:
                        self.conncountCallback(self.online_count)
                    self.epoll.unregister(fd)
                    rsocket.close()
                    del self.cSocketDict[fd]

    def close(self):
        self.__bLoop = False
        self.epoll.unregister(self.sSocket.fileno())
        self.sSocket.close()
        self.epoll.close()


    def send_data(self, data):
        for key in self.cSocketDict:
            if key != self.sSocket.fileno():
                self.cSocketDict[key].send(data)



if __name__ == "__main__":
    def recvdata(data):
        print(data)

    def online_count_show(count):
        print('在线客户端数：', count)

    print('start sever...')
    server = ServerManager(('192.168.1.246', 5200), 5, recvdata, online_count_show)
    print('server is running')



