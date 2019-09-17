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
    
    def change_state(self, state):
        if state in ('chilling', 'inroom', 'playing'):
            self.state = state

class Room:
    def __init__(self, room_name):
        self.room_name = room_name
        self.triunf = None
        self.table = None
        self.players = []
        self.deck = None
        self.state = 'waiting' #going
    
    def change_state(self, state):
        if state in ('waiting', 'going'):
            self.state = state
    
    def connect_player(self, player):
        if len(self.players) < 3:
            self.players.append(player)
            return True
        return False
    
    def disconnet_player(self, player):
        self.players.remove(player)
    
    def get_players_in_room(self):
        return self.players
    

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
        return rooms

    
    def get_players(self):
        players = []
        for name in self.players.keys():
            players.append(name)
        return players
    

    def evaluate_request(self, socket):
        request = socket.request
        print(socket.addr, request)
        close = False
        action = request['action']
        user = request['user']
        if action == 'login':
            print("agregar usuario")
            player = Player(socket, user)
            if user not in self.players.keys():
                self.players[user] = player
                print("usuario agregado")
                content = {"status":"login", "rooms":self.get_rooms(), "players": self.get_players()}
            else:
                print("usuario ya existe")
                content = {"status":"error", "message": f'User "{user}" exists'}
                close = True

        elif user in self.players.keys():
            if action == 'get_rooms':
                print("mostrar rooms")
                content = {"status":"get_rooms", "rooms":self.get_rooms()}

            elif action == 'create_room':
                print("agregar room")
                room_name = request['room']
                room = Room(room_name)
                if room_name not in self.rooms.keys():
                    self.rooms[room_name] = room
                    print("room agregado")
                    #content = {"status":"create_room", "rooms":self.get_rooms()}
                    content = {"status":"get_rooms", "rooms":self.get_rooms()}
                else:
                    print("room ya existe")
                    content = {"status":"error", "message": f'Room "{room_name}" exists'}

            elif action == 'join_room':
                print("usuario unido a room")
                room_name = request['room']
                if room_name in self.rooms.keys():
                    if (self.rooms[room_name].connect_player(user)):
                        self.players[user].change_state('inroom')
                        content = {"status":"join_room", "room":room_name ,"players_in_room": self.rooms[room_name].get_players_in_room()}
                    else:
                        content = {"status":"error", "message": f'Room "{room_name}"is full'}

                else:
                    content = {"status":"error", "message": f'Room "{room_name}"doesnt exists'}

            elif action == 'get_players':
                print("mostrar jugadores")
                content = {"status":"get_players", "players": self.get_players()}

            elif action == 'disconnect':
                print("bye player")
                self.players.pop(user)
                content = {"status":"disconnect"}
                close = True

            #TODO: enviar y recibir mensajes (chat)
            #TODO: logica del juego
            else:
                content = {"status":"error", "message": f'Command "{action}" doesnt exists'}
        else:
                content = {"status":"error", "message": 'login first'}

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

