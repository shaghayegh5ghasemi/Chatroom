import threading
import socket
import os
import socketserver


class tcpserverthread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', cPort))
            s.listen()
            while (True):
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024)
                    strdata = data.decode('utf-8')
                    parseddata = strdata.split("-")
                    if (parseddata[0] == "txt"):
                        sender = parseddata[1]
                        txt = parseddata[2]
                        print(sender, ": ", txt)
                        print("")
                    else:
                        if (parseddata[0] == "file"):
                            filename=parseddata[2]
                            print(parseddata[1], " is sending a file: ")
                            file = open(filename, 'wb')
                            l = conn.recv(1024)
                            while (l):
                                file.write(l)
                                l = conn.recv(1024)
                            print("file has been recieved")
                            file.close()
                        else:
                            if (parseddata[0] == "changename"):
                                result = parseddata[1]
                                if (result == "successful"):
                                    print("Your name has been changed successfully")
                                else:
                                    print("The name you entered exists among contacts")
                            else:
                                if (parseddata[0] == "show"):
                                    connectedusers = parseddata[1]
                                    print(parseddata[1])
                                else:
                                    if(parseddata[0]=="connected"):
                                        print(parseddata[1], "in now online")
                                    else:
                                        if(parseddata[0]=="disconnected"):
                                            print(parseddata[1], "in now offline")
                                        else:
                                            if(parseddata[0]=="deleted"):
                                                print(parseddata[1], "has left the chat")


class handshaketoserver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        s = socket.socket()
        s.connect((addr, sPort))
        msg = "handshake" + "-" + name + "-" + myip + "-" + str(cPort) + "-" + password
        bytemsg = bytes(msg, 'utf-8')
        s.send(bytemsg)
        a = s.recv(1024).decode('utf-8')
        handshakeresult['status'] = a
        s.close()


addr = input("Please enter the server address: ")
sPort = int(input("Please enter the Port of server: "))
name = input("Please enter your username: ")
password = input("Please enter your password: ")
cPort = int(input("Please enter your desired port for connection: "))
myip = "127.0.0.1"  # u can use os library to find your ip in practice

tcpserver = tcpserverthread()
handshakeresult = {}
handshake = handshaketoserver()
handshake.start()
handshake.join()
while (handshakeresult['status'] == "exist"):
    print("Username and password does not match. (if you are a new user, enter new username for creating acoount)")
    name = input("Please enter your username: ")
    password = input("Please enter your password: ")
    cPort = int(input("Please enter your desired port for connection "))
    handshake = handshaketoserver()
    handshake.start()
    handshake.join()
print("connected to server succesfully!")
tcpserver.start()

while (True):
    choice = input("please enter your command:\n")
    if (choice.lower() == "show"):
        s = socket.socket()
        s.connect((addr, sPort))
        msg = "show" + "-" + name
        bytemsg = bytes(msg, 'utf-8')
        s.send(bytemsg)
        s.close()
    else:
        if (choice.lower() == "send"):
            s = socket.socket()
            s.connect((addr, sPort))
            contact = input("Who do you want to send?")
            msgtype = input("Do you want to send message or file (m/f)? ")
            if (msgtype.lower() == "m"):
                txt = input("Enter your message: ")
                msg = "send" + "-" + contact + "-" + txt + "-" + name
                bytemsg = bytes(msg, 'utf-8')
                s.send(bytemsg)
            else:
                if (msgtype.lower() == "f"):
                    filepath = input("Enter your file path: ")
                    msg="sendfile"+"-"+contact+"-"+filepath+"-"+name
                    bytemsg = bytes(msg, 'utf-8')
                    s.send(bytemsg)
                    status=s.recv(1024)
                    status = status.decode("utf8")
                    if(status=="ready"):
                        file = open(filepath, "rb")
                        l = file.read(1024)
                        while (l):
                            s.send(l)
                            l = file.read(1024)
                        file.close()
                    else: print("sending file is not possible")
                    s.close()
        else:
            if (choice.lower() == "changename"):
                newname = input("Enter your new username: ")
                s = socket.socket()
                s.connect((addr, sPort))
                msg = "changename" + "-" + newname + "-" + name + "-" + password
                bytemsg = bytes(msg, 'utf-8')
                s.send(bytemsg)
                s.close()
            else:
                if (choice.lower() == "quit"):
                    s = socket.socket()
                    s.connect((addr, sPort))
                    msg = "quit" + "-" + name + "-" + password
                    bytemsg = bytes(msg, 'utf-8')
                    s.send(bytemsg)
                    s.close()
                    os._exit(0)
                else:
                    if(choice.lower() == "delete"):
                        s = socket.socket()
                        s.connect((addr, sPort))
                        msg = "delete" + "-" + name + "-" + password
                        bytemsg = bytes(msg, 'utf-8')
                        s.send(bytemsg)
                        s.close()
                        os._exit(0)
                    else:
                        if (choice.lower() == "show"):
                            s = socket.socket()
                            s.connect((addr, sPort))
                            msg = "show" + "-" + name + "-" + password
                            bytemsg = bytes(msg, 'utf-8')
                            s.send(bytemsg)
                            s.close()
                            os._exit(0)
                        else:
                            print("invalid input")
