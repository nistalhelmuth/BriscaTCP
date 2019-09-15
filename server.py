import sys
import socket
import selectors
import traceback

import lib

class Player:
    def __init__(self, socket, user_name):
        self.socket = socket
        self.user_name = user_name
        self.state = 'chilling' #inroom - playing

class Room:
    def __init__(self, room_name):
        self.room_name = room_name
        self.triunf = None
        self.table = None
        self.players = []
        self.deck = None
        self.state = 'waiting' #going

class Server:
    def __init__(self, host='127.0.0.1', port=3000):
        print("listening on", (host, port))
        self.sel = selectors.DefaultSelector()
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lsock.bind((host, port))
        self.lsock.listen()
        self.lsock.setblocking(False)
        self.sel.register(self.lsock, selectors.EVENT_READ, data=None)
        self.players = {}
        self.rooms = {}
    
    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print("accepted connection from", addr)
        conn.setblocking(False)
        socket = lib.SocketHandler(self.sel, conn, addr)
        self.sel.register(conn, selectors.EVENT_READ, data=socket)

    
    def get_rooms(self):
        rooms = []
        for name in self.rooms.keys():
            rooms.append(name)
        return self.rooms

    
    def get_players(self):
        players = []
        for name in self.players.keys():
            players.append(name)
        return players
    

    def evaluate_request(self, socket):
        request = socket.request
        print(socket.addr, request)
        close = False
        value = request['value']
        action = request['action']
        if action == 'login':
            print("agregar usuario")
            user = Player(socket, value)
            if value not in self.players.keys():
                self.players[value] = user
                print("usuario agregado")
                content = {"status":"ok", "rooms":self.get_rooms(), "players": self.get_players()}
            else:
                print("usuario ya existe")
                content = {"status":"error", "message": f'User "{value}" exists'}
                close = True

        elif action == 'get_rooms':
            print("mostrar rooms")
            content = {"status":"ok", "rooms":self.get_rooms()}

        elif action == 'create_room':
            print("agregar room")
            room = Room(value)
            if value not in self.rooms.keys():
                self.rooms[value] = room
                print("room agregado")
                content = {"status":"ok", "rooms":self.get_rooms()}
            else:
                print("room ya existe")
                content = {"status":"error", "message": f'Room "{value}" exists'}

        elif action == 'join_room':
            print("agregar a room")
            print("agregar cambiar estado")

        elif action == 'get_players':
            print("mostrar jugadores")
            content = {"status":"ok", "players": self.get_players()}

        elif action == 'disconnect':
            print("bye player")
            content = {"status":"ok"}
            close = True

        else:
            content = {"status":"error", "message": f'Command "{action}" doesnt exists'}

        socket.write(content)
        if close:
            socket.close()
    

    def start(self):
        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        socket = key.data
                        try:
                            if mask & selectors.EVENT_READ:
                                socket.read()
                            if mask & selectors.EVENT_WRITE:
                                self.evaluate_request(socket)
                        except Exception:
                            print(
                                "main: error: exception for",
                                f"{socket.addr}:\n{traceback.format_exc()}",
                            )
                            socket.close()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
           self.sel.close()


server = Server()
server.start()

