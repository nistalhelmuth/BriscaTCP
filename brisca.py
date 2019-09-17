

class Player:
    def __init__(self, socket, user_name):
        self.socket = socket
        self.user_name = user_name
        self.state = 'chilling' #inroom - playing
    
    def change_state(self, state):
        if state in ('chilling', 'inroom', 'playing'):
            self.state = state
    
    def write(self, content):
        self.socket.write(content)
    
    def get_user_name(self):
        return self.user_name

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
    
    def connect_player(self, new_player):
        if len(self.players) < 3 and new_player not in self.players:
            for player in self.players:
                print("sending entered",player.get_user_name())
                content = {"status":"player_entered", "room":self.room_name, "new_player": new_player.get_user_name()}
                player.write(content)
            self.players.append(new_player)
            return True
        return False
    
    def disconnet_player(self, player):
        self.players.remove(player)
    
    def get_players_in_room(self):
        players = []
        for player in self.players:
            players.append(player.get_user_name())
        return players
    
    def send_message_to_all(self, content):
        for player in self.players:
            player.write(content)
#class Brisca:
#  class Game:
#    triunfo: carta intercambiable
#    mesa: selecciones de las jugadores
#    punteos: puntajes de los jugadores
#    jugadores: quienes son los jugadores
#    baraja: cartas a repartir
#    estado: esperando o jugando
#
#  
#  class Player:
#    sock
#    nombre: identificador defindo
#    estado: chilling, ready, playing
#
#lista de jugadores
#lista de juegos
#
#
## chat
## rooms
## game
#
##servidor incia
#'''
#jugador se conecta
#jugador puede pedir:
#  lista de salas
#  lista de jugadores
#  crear sala
#  unirse a sala
#jugador se desconecta
#'''
#
##room 
#'''
#mostrar quienes estan conectados
#cambiar estado de jugador a listo
#'''
#
##game
#'''
#repartir 3 cartas a cada uno
#mostrar triunfo
#recibir el cambio del triunfo
#mostrar mesa
#comparar todas las selecciones
#acumular puntos
#*repartir
#mostrar resultados
#'''
#
##chat
#'''
#difundir directo
#difundir mensaje para sala
#'''