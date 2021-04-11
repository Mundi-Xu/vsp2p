##################################################################################
# Author: Mundi Xu                                                               #
# Version: 0.1 beta (use at your own risk)                                       #
#                                                                                #
# A very simple Tracker server, the file list is append-only                     #
# using the pickle library to serialize data may cause RCE                       #
# so please only allow trusted nodes to connect.                                 #
##################################################################################

import pickle
import threading
from datetime import datetime
from socket import *
from threading import *

PORT = 8080
HOST = "localhost"
MAXCONNECTION = 5
REGISTER = '1'
SEARCH = '2'
DOWNLOAD = '3'
LIST_ALL = '4'
EXIT = '5'


class Tracker(threading.Thread):
    def __init__(self, host, port, max_connection):
        threading.Thread.__init__(self)
        self.host = host
        self.semaphore = Semaphore(max_connection)
        self.port = port
        self.sock = socket()
        self.sock.bind((self.host, self.port))
        self.sock.listen(max_connection)
        self.Files = []
        self.keys = ['peer_id', 'file_name', 'Date_added']
        print("Tracker Start listening on", self.host, ":", self.port)

    def run(self):
        while True:
            conn, addr = self.sock.accept()
            print("收到请求 ", addr[0], ":", addr[1])
            request = pickle.loads(conn.recv(1024))

            if request[0] == REGISTER:
                print("Peer", addr[1], ", 添加新文件\n")
                self.semaphore.acquire()
                self.register(request[1], request[2], str(datetime.now()))
                ret = "File Registered Successfully,"
                conn.send(bytes(ret, 'utf-8'))
                self.semaphore.release()
                conn.close()

            elif request[0] == SEARCH:
                print("Peer", addr[1], ", 查询文件\n")
                self.semaphore.acquire()
                ret_data = pickle.dumps(self.Search_data(request[1]))
                conn.send(ret_data)
                self.semaphore.release()
                conn.close()

            elif request[0] == LIST_ALL:
                print("Peer", addr[1], ", 返回所有文件\n")
                self.semaphore.acquire()
                ret_data = pickle.dumps(self.all_data())
                conn.send(ret_data)
                self.semaphore.release()
                conn.close()

            else:
                continue

    def register(self, peer_id, file_name, Date):
        '''
            [peer_id, file_name, Date_added]
        '''

        entry = [str(peer_id), file_name, str(Date)]
        self.Files.insert(0, dict(zip(self.keys, entry)))

    def Search_data(self, file_name):
        ret = []
        for item in self.Files:
            if item['file_name'] == file_name:
                entry = [item['peer_id'],
                         item['file_name'], item['Date_added']]
                ret.insert(0, dict(zip(self.keys, entry)))
        return ret, self.keys

    def all_data(self):
        return self.Files, self.keys


def Start():
    print("\nTracker服务器启动成功\n")
    server = Tracker(HOST, PORT, MAXCONNECTION)
    server.start()


if __name__ == '__main__':
    Start()
