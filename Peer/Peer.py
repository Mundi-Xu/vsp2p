##################################################################################
# Author: Mundi Xu                                                               #
# Version: 0.1 beta (use at your own risk)                                       #
#                                                                                #
# A very simple p2p file transfer program                                        #
#                                                                                #
# using the pickle library to serialize data may cause RCE                       #
# so please upload or download only trusted files.                               #
##################################################################################


from Node import *
import sys

sys.path.insert(0, '..')  # Import the files where the modules are located


class Peer:
    def __init__(self):
        print("Input one of the following command:\n")
        while True:

            msg = input('''Input one of the following command:\n 
                1. register [peerID] [filename] ----register a file to server\n
                2. search [filename] ---------------request server for the peers info which have the requested file \n
                3. download [peerID] [filename] ----download file on the peers \n
                4. list all ------------------------show all sharing files that registered\n 
                5. exit  ---------------------------exit the client \n''')

            if not msg:
                break
            cmd = msg.split()

            if cmd[0] == REGISTER:
                Peer_id = cmd[1]  # 获取peer id
                self.file_name = cmd[2]  # 获取要分享的文件
                self.Peer_port = int(Peer_id)
                self.register()  # 连接Tracker并注册文件
                Start_Node(self.Peer_port,
                           HOST)

            elif cmd[0] == SEARCH:
                file_name = cmd[1]

                self.search(file_name)

            elif cmd[0] == DOWNLOAD:

                Peer_id = cmd[1]
                file_name = cmd[2]
                self.download(int(Peer_id), file_name)

            elif cmd[0] == LIST_ALL:  # 查询所有正在共享的文件
                self.List_all()

            elif cmd[0] == EXIT:
                break
            else:
                print("ignored!")
                continue
        
        sys.exit(0)

    def register(self):
        s = socket()
        s.connect((TRACKERHOST, PORT))
        data = pickle.dumps(self.formatData(self.Peer_port, self.file_name))
        s.send(data)
        state = s.recv(1024)
        print(state.decode('utf-8'))  # 返回信息
        s.close()

    def search(self, file_name):
        s = socket()
        s.connect((TRACKERHOST, PORT))
        fdata = [SEARCH, file_name]
        data = pickle.dumps(fdata)
        s.send(data)
        ret_data = pickle.loads(s.recv(1024))

        self.print_list(ret_data[0], ret_data[1])
        s.close()

    def download(self, Peer_id, file_name):
        s = socket()
        s.connect((HOST, Peer_id))
        data = pickle.dumps([DOWNLOAD, str(file_name)])
        s.send(data)

        # 确定共享文件路径
        file_path = os.path.join(os.getcwd(), '..')
        file_path = os.path.join(file_path, FILEPATH)
        file_path = os.path.join(file_path, DOWNLOADDIR)

        with open(os.path.join(file_path, file_name),
                  'wb') as myfile:
            while True:
                data = s.recv(1024)
                if not data:
                    myfile.close()
                    break
                myfile.write(data)
        s.close()
        print("文件下载完成")

    def List_all(self):
        s = socket()
        s.connect((TRACKERHOST, PORT))
        data = pickle.dumps(str(LIST_ALL))
        s.send(data)
        ret_data = pickle.loads(s.recv(1024))
        self.print_list(ret_data[0], ret_data[1])
        s.close()

    def formatData(self, Peer_port, file_name):  # 将数据转换为列表
        return [REGISTER, Peer_port, file_name]

    def print_list(self, Files, keys):
        if len(Files) > 0:
            print("Peer_Id  |     File_name    |  Date_added :\n")
            for item in Files:
                print("  ", item[keys[0]], "       ",
                      item[keys[1]], "   ", item[keys[2]])
        else:
            print("There is no file has this name Or There is no file At all\n")


def Start_Peer():
    peer = Peer()


if __name__ == '__main__':
    Start_Peer()
