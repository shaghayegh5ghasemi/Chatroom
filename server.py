import threading
import socket
import time

def getUsers():
    userfile = open("users.txt", 'r')
    while True:
        line = userfile.readline()
        if not line:
            break
        user = line.split(" ")
        # username ip port password
        connectedusers[user[0]] = [(user[1], int(user[2])), user[3][:-1]]
    userfile.close()


def updateUsers():
    userfile = open("users.txt", 'w')
    for key, values in connectedusers.items():
        print(values)
        userfile.write(key + " " + str(values[0][0]) + " " + str(values[0][1]) + " " + values[1])
        userfile.write("\n")


class clinetHandler(threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr

    def run(self):
        with self.conn:
            data = self.conn.recv(1024)
            # convert byte to string
            strdata = data.decode('utf-8')
            parseddata = strdata.split("-")
            if (parseddata[0] == "handshake"):
                if parseddata[1] in connectedusers.keys():
                    if parseddata[4] != connectedusers[parseddata[1]][1]:
                        msg = "exist"
                        bytemsg = bytes(msg, 'utf-8')
                        self.conn.send(bytemsg)
                    else:
                        msg = "connected"
                        bytemsg = bytes(msg, 'utf-8')
                        self.conn.send(bytemsg)
                        # inform other users
                        connectedusers[parseddata[1]] = [(parseddata[2], int(parseddata[3])), parseddata[4]]
                        onlineUsers[parseddata[1]] = connectedusers[parseddata[1]]
                        updateUsers()
                        getUsers()
                        print(connectedusers)
                        print("user with name of ",
                              parseddata[1], " is online")
                        for key, values in onlineUsers.items():
                            msg = "connected"+"-"+parseddata[1]
                            message = sendmsgthread(msg, onlineUsers[key][0])
                            message.start()
                else:
                    # inform other users
                    for key, values in onlineUsers.items():
                        msg = "connected" + "-" + parseddata[1]
                        message = sendmsgthread(msg, onlineUsers[key][0])
                        message.start()
                    connectedusers[parseddata[1]] = [(parseddata[2], int(parseddata[3])), parseddata[4]]
                    onlineUsers[parseddata[1]] = connectedusers[parseddata[1]]
                    updateUsers()
                    getUsers()
                    print("user with name of ",
                          parseddata[1], " connected to server")
                    #print(onlineUsers)
                    msg = "connected"
                    bytemsg = bytes(msg, 'utf-8')
                    self.conn.send(bytemsg)
            else:
                if (parseddata[0] == "send"):
                    rec = parseddata[1]
                    sen = parseddata[3]
                    txt = parseddata[2]
                    print(sen, "is sending a message to ", rec)
                    msg = "txt" + "-" + sen + "-" + txt
                    s1 = sendmsgthread(msg, onlineUsers[rec][0])
                    s1.start()
                else:
                    if (parseddata[0] == "sendfile"):
                        rec = parseddata[1]
                        sen = parseddata[3]
                        filename = parseddata[2] + str(time.time()) + ".txt"
                        msg="ready"
                        bytemsg = bytes(msg, 'utf-8')
                        self.conn.send(bytemsg)
                        print(sen, " is sending a file to ", rec)
                        file=open(str(time.time()) + ".txt", 'wb')
                        l = self.conn.recv(1024)
                        while (l):
                            file.write(l)
                            l = self.conn.recv(1024)
                        file.close()
                        msg = "file" + "-" + sen + "-" + filename
                        s1 = sendmsgthread(msg, onlineUsers[rec][0])
                        s1.start()
                        transfer = sendfilethread(filename, onlineUsers[rec][0])
                        transfer.start()
                    else:
                        if (parseddata[0] == "changename"):
                            name = parseddata[2]
                            if (parseddata[1] in connectedusers.keys()):
                                msg = "changename" + "-" + "exist"
                                s1 = sendmsgthread(msg, onlineUsers[parseddata[1]][0])
                                s1.start()
                            else:
                                if (onlineUsers[parseddata[2]][1] == parseddata[3]):
                                    connectedusers[parseddata[1]] = connectedusers[name]
                                    onlineUsers[parseddata[1]] = onlineUsers[name]
                                    del connectedusers[name]
                                    del onlineUsers[name]
                                    updateUsers()
                                    getUsers()
                                    msg = "changename" + "-" + "successful"
                                    print(name, "has changed to ", parseddata[1])
                                    s1 = sendmsgthread(msg, onlineUsers[parseddata[1]][0])
                                    s1.start()
                        else:
                            if (parseddata[0] == "show"):
                                name = parseddata[1]
                                print('showing contact list to ', name)
                                users=[]
                                for key, values in onlineUsers.items():
                                    users.append(key)
                                msg = "show" + "-" + str(users)
                                s1 = sendmsgthread(msg, connectedusers[parseddata[1]][0])
                                s1.start()
                            else:
                                if (parseddata[0] == "quit"):
                                    name = parseddata[1]
                                    password = parseddata[2]
                                    if (onlineUsers[name][1] == password):
                                        del onlineUsers[name]
                                        print(name, "is offline")
                                        for key, values in onlineUsers.items():
                                            msg = "disconnected" + "-" + parseddata[1]
                                            message = sendmsgthread(msg, onlineUsers[key][0])
                                            message.start()
                                else:
                                    if (parseddata[0] == "delete"):
                                        name = parseddata[1]
                                        password = parseddata[2]
                                        if (onlineUsers[name][1] == password):
                                            del onlineUsers[name]
                                            del connectedusers[name]
                                            print(name, "left")
                                            for key, values in onlineUsers.items():
                                                msg = "deleted" + "-" + parseddata[1]
                                                message = sendmsgthread(msg, onlineUsers[key][0])
                                                message.start()
                                            updateUsers()
                                            getUsers()


class tcpserverthread(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        self.port = int(port)

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', self.port))
            s.listen()
            while (True):
                # conn = soucket, addr = ip
                conn, addr = s.accept()
                client = clinetHandler(conn, addr)
                client.start()


class sendmsgthread(threading.Thread):
    def __init__(self, msg, addr):
        threading.Thread.__init__(self)
        self.msg = msg
        self.addr = addr

    def run(self):
        s2 = socket.socket()
        s2.connect(self.addr)
        bytemsg = bytes(self.msg, 'utf-8')
        s2.send(bytemsg)
        s2.close()

class sendfilethread(threading.Thread):
    def __init__(self, filename, addr):
        threading.Thread.__init__(self)
        self.filename = filename
        self.addr = addr

    def run(self):
        s2 = socket.socket()
        s2.connect(self.addr)
        file = open(self.filename, "rb")
        l = file.read(1024)
        while (l):
            s2.send(l)
            l = file.read(1024)
        file.close()
        s2.close()

connectedusers = {}
onlineUsers = {}
getUsers()
port = input("Set Server port:")
tcpserver = tcpserverthread(port)
tcpserver.start()
print("Server started listening on port : " + port)
print("ALL USERS: ")
print(connectedusers)

if(input() == "show"):
    print(onlineUsers)
