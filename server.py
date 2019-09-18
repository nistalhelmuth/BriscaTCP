import sys
import socket
import selectors
import traceback
import lib
from brisca import Room, Player


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

    def message_to_room(self, content, room):
        room = self.rooms[room]
        if room:
            room.send_message_to_all(content)
            return True
        return False

    def message_to_player(self, content, player):
        player = self.players[player]
        if player:
            player.write(content)
            return True
        return False

    def evaluate_request(self, socket):
        request = socket.request
        print(socket.addr, request)
        close = False
        write = True
        action = request['action']
        user = request['user']
        if action == 'login':
            print("agregar usuario")
            player = Player(socket, user)
            if user not in self.players.keys():
                self.players[user] = player
                print("usuario agregado")
                content = {"status": "login", "rooms": self.get_rooms(
                ), "players": self.get_players()}
            else:
                print("usuario ya existe")
                content = {"status": "error",
                           "message": f'User "{user}" exists'}
                close = True

        elif user in self.players.keys():
            if action == 'get_rooms':
                print("mostrar rooms")
                content = {"status": "get_rooms", "rooms": self.get_rooms()}

            elif action == 'create_room':
                print("agregar room")
                room_name = request['room']
                room = Room(room_name)
                if room_name not in self.rooms.keys():
                    self.rooms[room_name] = room
                    print("room agregado")
                    content = {"status": "room_created",
                               "rooms": self.get_rooms()}
                else:
                    print("room ya existe")
                    content = {"status": "error",
                               "message": f'Room "{room_name}" exists'}

            elif action == 'join_room':
                print("usuario unido a room")
                room_name = request['room']
                if room_name in self.rooms.keys():
                    connected = self.rooms[room_name].connect_player(
                        self.players[user])
                    if connected:
                        self.players[user].change_state('inroom')
                        content = {"status": "join_room", "room": room_name,
                                   "players_in_room": self.rooms[room_name].get_players_in_room()}
                        socket.write(content)
                        write = False
                        self.rooms[room_name].try_start()
                    else:
                        content = {"status": "error",
                                   "message": f'Room "{room_name}"is full'}

                else:
                    content = {"status": "error",
                               "message": f'Room "{room_name}"doesnt exists'}

            elif action == 'get_players':
                print("mostrar jugadores")
                content = {"status": "get_players",
                           "players": self.get_players()}

            elif action == 'message_to_room':
                print("enviar mensaje a room")
                room = request['room']
                message = request['message']
                content = {"status": "message_to_room",
                           "from": user, "room": room, "message": message}
                if(self.message_to_room(content, room)):
                    content = {"status": "message_to_room_sent",
                               "from": user, "room": room, "message": message}
                else:
                    content = {"status": "error",
                               "message": 'couldnt send message to room'}

            elif action == 'message_to_player':
                print("enviar mensaje a jugador")
                to = request['to']
                message = request['message']
                content = {"status": "message_to_player",
                           "from": user, "to": to, "message": message}
                if (self.message_to_player(content, to)):
                    content = {"status": "message_to_player_sent",
                               "from": user, "to": to, "message": message}
                else:
                    content = {"status": "error",
                               "message": 'couldnt send message to player'}

            elif action == 'card_pick':
                print('seleccion del jugador')
                room = request['room']
                pick = request['card']
                player_name = user
                if room in self.rooms.keys():
                    self.rooms[room].card_pick(pick, player_name)
                    write = False
                else:
                    content = {"status": "error",
                               "message": 'room doesnt exists'}

            elif action == 'disconnect':
                print("bye player")
                self.players.pop(user)
                content = {"status": "disconnect"}
                close = True

            # TODO: enviar y recibir mensajes (chat)
            # TODO: logica del juego
            else:
                content = {"status": "error",
                           "message": f'Command "{action}" doesnt exists'}
        else:
            content = {"status": "error", "message": 'login first'}

        if write:
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
