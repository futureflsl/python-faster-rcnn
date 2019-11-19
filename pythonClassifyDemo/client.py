# encoding: utf-8
import threading
import socket
import time

SEND_BUF_SIZE = 102400
RECV_BUF_SIZE = 102400


class PresenterSocketClient(object):
    def __init__(self, server_address, reconnectiontime=5,recvCallback=None):
        self._server_address = server_address
        self._reconnectiontime = reconnectiontime
        self.__recvCallback = recvCallback
        self._sock_client = None
        self._bstart = True
        # threading.Thread(target=self.start_connect()).start()

    def start_connect(self):
        print("创建socket对象...")
        self._sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock_client.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SEND_BUF_SIZE)
        self._sock_client.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, RECV_BUF_SIZE)
        try:
            print("连接服务器...")
            self._sock_client.connect(self._server_address)
        except Exception as e:
            print(e)
            print("正在重新连接...")
            time.sleep(self._reconnectiontime)
            self.start_connect()
            return
        self._bstart = True
        print("监听数据接受中...")
        threading.Thread(target=self.__start_listenning()).start()

    def __start_listenning(self):
        while self._bstart:
            try:
                # print("等待数据到达...")
                data = self._sock_client.recv(RECV_BUF_SIZE)
                if data:
                    if self.__recvCallback:
                        self.__recvCallback(data)
                    #print(data)
                    # self.send_data("hello".encode())
                else:
                    print("close")
                    self._sock_client.close()
                    self.start_connect()
                    break
            except Exception as e:
                print(e)
                self._sock_client.close()
                self.start_connect()
                break

    def send_data(self, data):
	# print(data)
        self._sock_client.sendall(data)

    def close(self):
        self._bstart = False
        self._sock_client.shutdown()
        self._sock_client.close()


if __name__ == "__main__":
    print('start client...')
    psc = PresenterSocketClient(("192.168.1.246", 5200))
    threading.Thread(target=psc.start_connect).start()
    print('client is running...')
    while True:
        data = raw_input('please input data you need to send:')
        psc.send_data(str.encode(data))
