import threading
import time


class A(object):
    def __init__(self):
        threading.Thread(target=self.dowork).start()
    def dowork(self):
        while True:
            print('sssssss')
            time.sleep(2)


if __name__ == "__main__":
    a = A()
    print('shit')