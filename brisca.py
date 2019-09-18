from random import randint

CARDS = ["clubs_1", "clubs_2", "clubs_3", "clubs_4", "clubs_5", "clubs_6", "clubs_7", "clubs_10", "clubs_11", "clubs_12", 
        "hearts_1", "hearts_2", "hearts_3", "hearts_4", "hearts_5", "hearts_6", "hearts_7", "hearts_10", "hearts_11", "hearts_12", 
        "spades_1", "spades_2", "spades_3", "spades_4", "spades_5", "spades_6", "spades_7", "spades_10", "spades_11", "spades_12",
        "diamonds_1", "diamonds_2", "diamonds_3", "diamonds_4", "diamonds_5", "diamonds_6", "diamonds_7", "diamonds_10", "diamonds_11", "diamonds_12"]

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
        self.table = None
        self.turn = 0
        self.round_picks = {}
        self.scores = {}
        self.players = []
        self.player_list = []
        self.deck = []
        self.state = 'waiting' #going
        self.cards = CARDS
    
    def change_state(self, state):
        if state in ('waiting', 'going'):
            self.state = state
    
    def create_deck(self):
        for i in range(0,40):
            u = randint(0, len(self.cards)-1)
            self.deck.append(self.cards.pop(u))

    def start_game(self):
        print("room ready",self.room_name)
        self.change_state('going')
        self.turn = randint(0, 3)
        self.create_deck()
        for player in self.players:
            content = {"status":"room_ready", "player":self.players[self.turn].user_name, "cards": self.deck[:3], "triunf": self.deck[-1]}
            self.player_list.append(player.get_user_name())
            self.scores[player.get_user_name()] = 0
            self.round_picks[player.get_user_name()] = ''
            self.deck = self.deck[3:]
            player.write(content)
    
    def try_start(self):
        if len(self.players) == 2: ##cambiar a 4
            self.start_game()
    
    def check_picks(self):
        triunf = CARDS.index(self.deck[-1])
        palo = int(triunf / 10)
        best = -1
        user = ''
        for player in self.round_picks.keys():
            card = self.round_picks[player]
            baza = CARDS.index(card)
            valor = int(baza / 10)
            if (palo == valor):
                new_best = (baza % 10)+10
                if (best < new_best):
                    best = new_best
                    user = player
            else:
                new_best = (baza % 10)
                if (best < new_best):
                    best = new_best
                    user = player
        return user
    
    def calculate_scores(self):
        for player in self.players.keys():
            pick = self.round_picks[player]
            baza = CARDS.index(pick)
            result = baza % 10
            if result == 0:
                self.scores[player] += 11
            if result == 2:
                self.scores[player] += 10
            if result == 7:
                self.scores[player] += 2
            if result == 8:
                self.scores[player] += 3
            if result == 9:
                self.scores[player] += 4
        self.round_picks = {}

    def finish_round(self):
        if len(deck) == 0:
            content = {"status":"game_finished"}
            for player in self.players:
                content[player.user_name] = self.scores[player.user_name]
                player.write(content)
        else:
            winner = self.check_picks()
            self.turn = 0 ###revisar self.player_list.index(winner)
            self.calculate_scores()
            for player in self.players:
                content = {"status":"round_finished", "winner": winner, "next_card":self.deck[:1]}
                self.deck = self.deck[1:]
                player.write(content)
    
    def card_pick(self, card, player_name):
        #validar si es el turno del chato que envia
        self.round_picks[player_name] = card
        self.turn = (self.turn + 1) % 4
        for player in self.players:
            content = {"status":"player_picked_card", "next_player":self.players[self.turn].user_name, "card": card, "picked":player_name}
            player.write(content)
        if len(self.round_picks) == 4:
            self.finish_round(self)


    
    def connect_player(self, new_player):
        if new_player not in self.players:
            if len(self.players) < 3:
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