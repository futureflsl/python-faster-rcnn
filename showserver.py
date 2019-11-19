#coding=utf-8

from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic.properties import QtGui

import server2 as tcpserver
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import pickle
import numpy as np


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.layout = QGridLayout(self)
        self.imagebox = QLabel('no result')
        self.imagesize = 0
        self.currentsize=0
        self.alldata=b''
        self.initializecomponent()
        self.server = tcpserver.ServerManager(('192.168.1.246', 5200), 5, self.recvdata, self.online_count_show)

    def img2pixmap(self, image):
        image = QImage(image, image.shape[1], image.shape[0], image.shape[1] * 3, QImage.Format_RGB888)
        pixmap = QPixmap(image)
        return pixmap

    def recvdata(self, data):
        nLen = len(data)
        print('data receive length:%d' % nLen)
        if nLen < 15:
            strlen = str(data)
            print(strlen)
            self.imagesize = int(strlen[2:-1])
            print('strlen:%s' % strlen[2:-1])
            print('image size is:%d' % self.imagesize)
            self.currentsize = 0
            self.alldata=b''
            self.server.send_data(b'send')
            return
        self.currentsize += nLen
        if self.currentsize < self.imagesize:
            self.alldata += data
        else:
            self.alldata += data
            print('final recive size is %d' % len(self.alldata))
            data = pickle.loads(self.alldata, encoding='bytes')
            # print(type(data))
            # image = QImage.fromData(data)
            # pixmap = QPixmap.fromImage(image)
            pixmap = self.img2pixmap(data)
            self.imagebox.setGeometry(0, 0, pixmap.width(), pixmap.height())
            self.imagebox.setPixmap(pixmap)
            self.server.send_data(b'over')

    def online_count_show(self, count):
        self.setWindowTitle("showserver-Current Clients Count is : %d" % count)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.server.close()
            event.accept()
        else:
            event.ignore()

    # 初始化UI界面控件
    def initializecomponent(self):
        self.setWindowTitle("showserver-Current Client Count is : 0")
        self.setFixedSize(600, 600)  # 设置窗体大小
        self.imagebox.setFixedSize(600, 600)  # 设置尺寸大小
        self.imagebox.setAlignment(QtCore.Qt.AlignCenter)  # 中心对齐
        self.imagebox.setStyleSheet('QWidget{background-color:rgb(0,255,0)}')  # 设置背景颜色
        self.layout.addWidget(self.imagebox)  # 添加控件


if __name__ == "__main__":
    app = QApplication(sys.argv)  # 新建QApplication实例
    mainWidget = MainWidget()  # 实例化一个类，继承自QWidget，也可以继承QMainWindow
    mainWidget.show()  # 显示窗口
    sys.exit(app.exec_())  # 进入消息主循环,sys.exit可以不写但是关闭窗口不会退出进程
