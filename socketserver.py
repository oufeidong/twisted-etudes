"""
Chat server with only select.
"""

import select, socket, sys

class ChatServer(object):
    def __init__(self, listener, name = "server"):
        self.listener = listener # listening socket
        self.name = name
        # self.socks = [self.listener]
        self.clients = [self.listener] # clients are Person objects (except for listener)
        # self.rooms = set()
        # self.peer2room = dict()
        self.msgqueues = dict()

    def start(self):
        while True:
            rlist, wlist, _ = select.select(self.clients, self.clients[1:], [])
                
            for rclient in rlist:
                if rclient is self.listener:
                    # Listener received connection request
                    self.handle_listener()
                else:
                    msg = self.get_msg(rclient)
                    self.handle_msg(rclient, msg)

            for wclient in wlist:
                while self.msgqueues[wclient]: # Is this loop necessary?
                    next_msg = self.msgqueues[wclient].pop()
                    wclient.sock.sendall(next_msg)

    def get_msg(self, client):
        # handles parsing messages
        cache = []

        while True:
            msg = client.sock.recv(10).decode()
            if not msg:
                self.clients.remove(client)
                break
            else:
                cache.append(msg)
                print("".join(cache))
                if msg.endswith("\n"):
                    break

        return "".join(cache)

    def handle_listener(self):
        sock, addr = self.listener.accept()
        client = Client(sock, addr)
        self.clients.append(client)
        self.msgqueues[client] = []
        print("{} has connected.".format(client.name))
        # Insert welcome message.

    def handle_msg(self, sender, msg): # sender = socket
        print("Client says:", msg)
        # room = self.peer2room[sender]
        for client in self.msgqueues:
            if client is not sender:
                self.msgqueues[client].append(msg.encode())

    def remove(self, client):
        client.sock.close()
        self.clients.remove(client)


class Room(object):
    def __init__(self, name):
        self.name = name
        self.clients = set()
        self.msgqueues = dict()

    # def add_client(self):
    #     pass

    def kick_client(self):
        pass


class Client(object):
    def __init__(self, sock, addr, name="anon"):
        self.sock = sock
        self.addr = addr
        self.name = name
        self.rooms = set()

    def set_name(self, name):
        self.name = name

    def join_room(self, room):
        room.clients.add(self)
        self.rooms.add(room)

    def leave_room(self, room):
        room.clients.remove(self)
        self.rooms.remove(room)

    def fileno(self):
        return self.sock.fileno()

def main():
    addr = ('127.0.0.1', 8000)

    # Create listening socket
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.setblocking(0)
    listener.bind(addr)
    listener.listen(5)

    print("Listening at", addr)

    server = ChatServer(listener)
    server.start()

if __name__ == '__main__':
    main()
