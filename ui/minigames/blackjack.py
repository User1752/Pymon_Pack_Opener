"""
Lógica do jogo Blackjack para integração com GUI.
"""
import random


class Card:
    """Representa uma carta de jogar."""
    
    SUITS = ['♠', '♥', '♦', '♣']
    RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    VALUES = {'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
              '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10}
    
    def __init__(self, rank, suit):
        """Inicializa uma carta com rank e naipe."""
        self.rank = rank
        self.suit = suit
        self.value = self.VALUES[rank]
    
    def __str__(self):
        """Retorna representação em string da carta."""
        return f"{self.rank}{self.suit}"
    
    def __repr__(self):
        """Retorna representação da carta."""
        return self.__str__()


class Deck:
    """Representa um baralho de cartas."""
    
    def __init__(self, num_decks=1):
        """Inicializa baralho com número especificado de baralhos."""
        self.cards = []
        for _ in range(num_decks):
            for suit in Card.SUITS:
                for rank in Card.RANKS:
                    self.cards.append(Card(rank, suit))
        random.shuffle(self.cards)
    
    def shuffle(self):
        """Baralha o baralho."""
        random.shuffle(self.cards)
    
    def deal(self):
        """Distribui uma carta do baralho."""
        if len(self.cards) == 0:
            # Se o baralho estiver vazio, cria um novo
            self.__init__()
        return self.cards.pop()


class Hand:
    """Representa uma mão de cartas."""
    
    def __init__(self):
        """Inicializa mão vazia."""
        self.cards = []
    
    def add_card(self, card):
        """Adiciona uma carta à mão."""
        self.cards.append(card)
    
    def get_value(self):
        """Calcula o valor da mão."""
        value = 0
        aces = 0
        
        for card in self.cards:
            if card.rank == 'A':
                aces += 1
                value += 11
            else:
                value += card.value
        
        # Ajusta para ases
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    def is_blackjack(self):
        """Verifica se a mão é um blackjack (21 com 2 cartas)."""
        return len(self.cards) == 2 and self.get_value() == 21
    
    def is_bust(self):
        """Verifica se a mão rebentou (passou de 21)."""
        return self.get_value() > 21
    
    def __str__(self):
        """Retorna representação em string da mão."""
        return ' '.join(str(card) for card in self.cards)
    
    def __repr__(self):
        """Retorna representação da mão."""
        return self.__str__()


class BlackjackGame:
    """Gere um jogo de blackjack."""
    
    def __init__(self, num_decks=1):
        """Inicializa um novo jogo."""
        self.deck = Deck(num_decks)
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.bet = 0
        self.game_over = False
    
    def deal_initial_cards(self):
        """Distribui duas cartas iniciais ao jogador e dealer."""
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
        self.player_hand.add_card(self.deck.deal())
        self.dealer_hand.add_card(self.deck.deal())
    
    def player_hit(self):
        """Jogador pede outra carta."""
        if not self.game_over:
            self.player_hand.add_card(self.deck.deal())
            if self.player_hand.is_bust():
                self.game_over = True
                return "bust"
        return "continue"
    
    def player_stand(self):
        """Jogador para, dealer joga."""
        if not self.game_over:
            # Dealer pede até 17 ou mais
            while self.dealer_hand.get_value() < 17:
                self.dealer_hand.add_card(self.deck.deal())
            
            self.game_over = True
            return self.determine_winner()
        return None
    
    def determine_winner(self):
        """Determina o vencedor do jogo."""
        player_value = self.player_hand.get_value()
        dealer_value = self.dealer_hand.get_value()
        
        if self.player_hand.is_bust():
            return "dealer"
        elif self.dealer_hand.is_bust():
            return "player"
        elif player_value > dealer_value:
            return "player"
        elif dealer_value > player_value:
            return "dealer"
        else:
            return "push"
    
    def reset(self):
        """Reinicia o jogo para uma nova ronda."""
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.game_over = False
        self.bet = 0


# Para compatibilidade com versão de consola
if __name__ == "__main__":
    print("This module is designed for GUI integration.")
    print("Please run pack_opener_gui_refactored.py to play Blackjack with GUI.")
