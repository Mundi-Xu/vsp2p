##################################################################################
# Author: Mundi Xu                                                               #
# Version: 0.1 beta (use at your own risk)                                       #
#                                                                                #
# A very simple Node server                                                      #
#                                                                                #
# using the pickle library to serialize data may cause RCE                       #
# so please only allow trusted nodes to connect.                                 #
##################################################################################

import os
import pickle
import threading
from socket import *
from threading import Semaphore

PORT = 8080 # Tracker的端口
HOST = "localhost"
TRACKERHOST = "localhost"
FILEPATH = "sharing"
UPLOADDIR = "uploads"
DOWNLOADDIR = "downloads"
MAXCONNECTION = 5
REGISTER = '1'
SEARCH = '2'
DOWNLOAD = '3'
LIST_ALL = '4'
EXIT = '5'


class Node(threading.Thread):
    def __init__(self, port, host, max_connection):
        threading.Thread.__init__(self)
        self.host = host
        self.semaphore = Semaphore(max_connection)  # 处理进程同步
        self.port = port  # 监听的端口号
        self.sock = socket()
        self.sock.bind((self.host, self.port))  # 绑定socket
        self.sock.listen(max_connection)

    def run(self):
        print("该节点正在共享文件\n")
        while True:
            conn, addr = self.sock.accept()
            print("建立连接 ", addr[0], ":", addr[1])
            request = pickle.loads(conn.recv(1024))
            if request[0] == DOWNLOAD:  # 确定共享文件路径
                file_path = os.path.join(os.getcwd(), '..')
                file_path = os.path.join(file_path, FILEPATH)
                file_path = os.path.join(file_path, UPLOADDIR)
                file_name = request[1]
                Full_path = os.path.join(file_path, file_name)
                self.semaphore.acquire()

                with open(Full_path, "rb") as myfile:  # 开始传输
                    while True:
                        f = myfile.read(2014)
                        while (f):
                            conn.send(f)
                            f = myfile.read(1024)
                        if not f:
                            myfile.close()
                            conn.close()
                            break
                self.semaphore.release()
                print("传输完成")
            else:
                continue


def Start_Node(port, host):
    peer = Node(port, host, MAXCONNECTION)
    peer.start()
