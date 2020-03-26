import itertools
import random
import time
import re
from StaticMethod import *


class Card:
    """ Class that defines a particular card.  Each card has a rank and suit.
    """
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.card = self.rank, self.suit

    def __repr__(self):
        return self.rank + "-" + self.suit


class Deck(set):
    """ Class that defines a standard deck of cards.  Each deck has the standard 52 cards,
    which consists of 13 ranks and 4 suits.  Class inherits from class set.
    """
    def __init__(self):
        """
        Generate a standard deck of cards and add to the set of cards.
        """
        super().__init__()
        for rank, suit in itertools.product(RANK_LIST, SUIT_LIST):
            self.add(Card(rank, suit))

    def get_card(self):
        """
        Return a card from the deck of cards.  This is accomplished by retrieving a random
        sample without replacement.  The chosen card is then removed from the deck.
        :return: Card
        """
        a_card = random.sample(self, 1)[0]
        self.remove(a_card)
        return a_card


class Player:
    """
    Class that defines a player's information and chips
    Attributes:
        hand: player's hand cards
        chips: the total chips of a player
        small_blind: the chips of a small blind need to bet
        big_blind: the chips of a big blind need to bet
        in_the_pot: chips that are already in the pot
        is_continue: if the player wants to continue playing for next round (False if the player folds)
    """
    def __init__(self, name, chips, small_blind, big_blind):
        self.name = name
        self.hand = []
        self.chips = chips
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.in_the_pot = 0
        self.is_continue = True

    def add_card(self, card):
        self.hand.extend(card)

    def get_hand(self):
        return self.hand

    def show_chips(self):
        print(f'Your total chips is ${self.chips}\nThe chips you bet or already in the pot is ${self.in_the_pot}\n')

    def get_hand_rank(self, community_cards):
        return get_highest_hand_rank(self.hand + community_cards)

    def bet(self, option, last_bet, addition_bet):
        """
        The player's action.
        Args:
            option: The player can check ('C'), call ('C'), raise ('R') or fold ('F')
            last_bet: last players bet
            addition_bet: the amount the player wants to raise
        Returns:
            The total amount of chips player bets
        """
        if option == 'C':
            self.in_the_pot = last_bet
        elif option == 'R':
            self.in_the_pot = last_bet + addition_bet
        else:
            self.hand = None
            self.is_continue = False
        return self.in_the_pot

    def start(self, blind):
        """
        When the game start, initialize the player's settings.
        Args:
            blind: ['Small', 'Big', None]  if the player is small blind, big blind or ordinary player
        """
        if blind == 'Small':
            self.in_the_pot = self.small_blind
        elif blind == 'Big':
            self.in_the_pot = self.big_blind
        else:
            self.in_the_pot = 0

    def restart(self, blind, rebuy=None):
        """
        Start the next game, settle the chips.
        Args:
            blind: ['Small', 'Big', None]  if the player is small blind, big blind or ordinary player
            rebuy: the amount of chips if the payer wants to buy in again
        """
        if rebuy:
            self.chips = rebuy
        self.is_continue = True
        self.hand = []
        if blind == 'Small':
            self.in_the_pot = self.small_blind
        elif blind == 'Big':
            self.in_the_pot = self.big_blind
        else:
            self.in_the_pot = 0


class Game(Deck):
    """
    The game settings for Texas Poker, including all the methods to run a Poker game.
    """
    def __init__(self, players, buy_in, small_blind, big_blind, blind=None, game_rule='Limited'):
        super().__init__()
        self.players = players
        self.chips = buy_in
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.last_bet = big_blind
        self.addition_bet = big_blind
        self.community_cards = []
        self.game_continue = True
        if not blind:
            choose_blind = random.randint(0, len(self.players)-1)  # randomly choose small blind player
        else:
            choose_blind = self.players.index(blind)
        self.index_small_blind = int(choose_blind)

        if self.index_small_blind == len(self.players) - 1:
            self.index_big_blind = 0
        else:
            self.index_big_blind = self.index_small_blind + 1

    def start_game(self):
        i = 0
        for player in self.players[:]:
            if i == self.index_small_blind:
                blind = 'Small'
            elif i == self.index_big_blind:
                blind = 'Big'
            else:
                blind = None

            exec(f'{player} = Player(\'{player}\', self.chips, self.small_blind, self.big_blind)')
            exec(f'{player}.start(blind)')
            i += 1

        players_temp = self.players
        self.players = []
        for player in players_temp:
            self.players.append(eval(player))
        # self.players = [eval(player) for player in self.players]

    def __player_bet(self, players_reorder):
        for player in players_reorder:
            print('-'*20 + '\n' + f'Player {player.name}\'s turn\n' + '-'*20)
            print(f'The community cards are: {self.community_cards}')
            print(f'Your hand cards are:{player.get_hand()}')
            player.show_chips()
            self.last_bet = player.bet(bet_option(), self.last_bet, self.addition_bet)

        players_reorder = [player for player in players_reorder[:] if player.is_continue]
        player_bets = [player.in_the_pot for player in players_reorder]

        if max(player_bets) != min(player_bets):
            return self.__player_bet(players_reorder)
        elif len(players_reorder) == 1:
            self.game_continue = False

    def pre_flop(self):
        print('-'*30 + '\nPre-flop\n' + '-'*30)
        time.sleep(1)
        if self.index_big_blind == len(self.players) - 1:
            index_order = 0
        else:
            index_order = self.index_big_blind + 1
        players_reorder = self.players[index_order:] + self.players[:index_order]

        for player in players_reorder:
            player.add_card([self.get_card() for x in range(2)])

        self.__player_bet(players_reorder)

    def flop(self):
        players_reorder = self.players[self.index_small_blind:] + self.players[:self.index_small_blind]
        players_reorder = [player for player in players_reorder[:] if player.is_continue]

        if not self.game_continue:
            self.__check_winner(players_reorder)
            return

        print('-' * 30 + '\nFlop\n' + '-' * 30)
        time.sleep(1)

        burn_card = self.get_card()
        self.community_cards = [self.get_card() for x in range(3)]

        self.__player_bet(players_reorder)

        self.addition_bet = self.addition_bet * 2

    def turn_river(self, round):
        players_reorder = self.players[self.index_small_blind:] + self.players[:self.index_small_blind]
        players_reorder = [player for player in players_reorder[:] if player.is_continue]

        if not self.game_continue:
            self.__check_winner(players_reorder)
            return

        print('-' * 30 + f'\n{round}\n' + '-' * 30)
        time.sleep(1)
        burn_card = self.get_card()
        self.community_cards.append(self.get_card())

        self.__player_bet(players_reorder)

    def __check_winner(self, players):
        if len(players) == 1:
            self.winner = players
            return

        hand_rank, comparators = get_highest_hand_rank(players[0].get_hand() + self.community_cards)
        winner = [players[0]]
        print(f'{players[0].name} got a {hand_rank}!')
        for player in players[1:]:
            hand_rank_new, comparators_new = get_highest_hand_rank(player.get_hand() + self.community_cards)
            print(f'{player.name} got a {hand_rank_new}!')
            if HAND_RANK.index(hand_rank_new) > HAND_RANK.index(hand_rank):
                winner = [player]
            elif HAND_RANK.index(hand_rank_new) == HAND_RANK.index(hand_rank):
                for comparator, comparator_new in zip(comparators, comparators_new):
                    if RANK_LIST.index(comparator_new) > RANK_LIST.index(comparator):
                        winner = [player]
                        break
                    elif RANK_LIST.index(comparator_new) == RANK_LIST.index(comparator):
                        if player not in winner:
                            winner = winner.append(player)
                        continue
                    else:
                        winner = [winner[0]]
                        break

            hand_rank = hand_rank_new
            comparators = comparators_new

        self.winner = winner

    def __check_chips(self):
        chips_in_pot = 0
        for player in self.players:
            chips_in_pot += player.in_the_pot
            player.chips -= player.in_the_pot
            player.in_the_pot = 0
        for winner in self.winner:
            winner.chips += chips_in_pot / len(self.winner)

    def showdown(self):
        players_reorder = self.players[self.index_small_blind:] + self.players[:self.index_small_blind]
        players_reorder = [player for player in players_reorder[:] if player.is_continue]

        if not self.game_continue:
            self.__check_winner(players_reorder)
            self.__check_chips()
            print(f'The winner is {self.winner[0].name}!')
            return

        print('-' * 30 + f'\nShowdown\n' + '-' * 30)
        time.sleep(1)
        print(f'The community cards are: {self.community_cards}')
        for player in players_reorder:
            # show hands and check winner
            print(f'{player.name}\'s hole cards are: {player.get_hand()}')

        print('\n')
        self.__check_winner(players_reorder)
        self.__check_chips()
        print(f'{[winner.name for winner in self.winner]} wins the game!')

    def show_players_chips(self):
        print('-' * 30 + '\nCheck Chips\n' + '-' * 30)
        time.sleep(1)
        for player in self.players:
            print(f'{player.name} still have ${player.chips}')

    def restart_game(self):
        super().__init__()
        self.index_small_blind = self.index_big_blind
        self.addition_bet = self.big_blind
        self.community_cards = []
        self.game_continue = True

        if self.index_small_blind == len(self.players) - 1:
            self.index_big_blind = 0
        else:
            self.index_big_blind = self.index_small_blind + 1

        i = 0
        for player in self.players[:]:
            is_continue = True if input(f'{player.name}, do you want to continue playing? (1 for yes)') == '1' else False
            if is_continue:
                reload = input(f'{player.name}, do you want to reload chips? (if so, input the chips in $ units)')
                try:
                    reload = float(reload)
                except:
                    reload = None
            else:
                del self.players[i]
                continue

            if i == self.index_small_blind:
                blind = 'Small'
            elif i == self.index_big_blind:
                blind = 'Big'
            else:
                blind = None

            player.restart(blind, reload)
            i += 1


if __name__ == '__main__':
    is_restart = True
    players = input('Please input players\' names: (split by \',\')')
    if players == '':
        players = ['Henry', 'Ahmad']
    else:
        players = re.split(r'\W+', players)
    
    while len(players) > 9 or len(players) < 2:
        print('The number of players is not valid!')
        players = input('Please input players\' names: (split by \',\')')
        if players == '':
            players = ['Henry', 'Ahmad']
        else:
            players = re.split(r'\W+', players)
    
    game = Game(players, 20, 0.1, 0.25)
    game.start_game()
    while is_restart:
        game.pre_flop()
        game.flop()
        game.turn_river('Turn')
        game.turn_river('River')
        game.showdown()
        game.show_players_chips()
        is_restart = True if input('Will the game move to the next round? (1 for yes)') == '1' else False
        if is_restart:
            game.restart_game()
