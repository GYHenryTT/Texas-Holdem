import collections

HAND_RANK = ("High-Card", "One-Pair", "Two-Pair", "3-of-a-Kind", "Straight", "Flush", "Full-House", "4-of-a-Kind",
             "Straight-Flush")
RANK_LIST = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")
SUIT_LIST = ("H", "S", "D", "C")


def bet_option():
    """
    Ask the player what the next action is.
    """
    option = input('Bet?: ("C" for call (check), "R" for raise, "F" for fold)').upper()
    if option in ('R', 'C', 'F'):
        return option
    else:
        print('Invalid input, please reenter!\n')
        return bet_option()


def get_highest_hand_rank(card_list):
    """
    Get the highest hand rank from a card list (length should be 7)
    """
    if len(card_list) != 7:
        raise ValueError('This method is only used on 7-card hand')
    rank_dict = collections.defaultdict(int)
    suit_dict = collections.defaultdict(int)
    for my_card in card_list:
        rank_dict[my_card.rank] += 1
        suit_dict[my_card.suit] += 1

    # sort the rank_dict by (rank_dict's value, RANK_LIST's index) reversely. It's a list of tuples like ('A', 4)
    rank_list = sorted(rank_dict.items(), key=lambda x: (x[1], RANK_LIST.index(x[0])), reverse=True)
    # sort the suit_list by suit_dict's value reversely. It's a list of tuples like ('H', 5)
    suit_list = sorted(suit_dict.items(), key=lambda x: x[1], reverse=True)

    # check for Full House or 4-of-a-kind
    if rank_list[0][1] == 4:
        kicker = sorted(rank_list[1:], key=lambda x: RANK_LIST.index(x[0]), reverse=True)[0]  # kicker is the biggest fifth card
        return "4-of-a-Kind", (rank_list[0][0], kicker)

    if rank_list[0][1] == 3 and rank_list[1][1] >= 2:
        return "Full-House", (rank_list[0][0], rank_list[1][0])

    # check for straight flush
    if suit_list[0][1] >= 5:
        flush = True
        check_straight = [card for card in card_list if card.suit == suit_list[0][0]]
    else:
        flush = False
        check_straight = card_list

    check_straight = set([card.rank for card in check_straight])
    check_straight = sorted(check_straight, key=lambda x: RANK_LIST.index(x), reverse=True)
    straight = False

    for i in range(len(check_straight) - 4):
        if RANK_LIST.index(check_straight[i]) - RANK_LIST.index(check_straight[i+4]) == 4:
            straight = True
            highest_card = check_straight[i]
            break
        else:
            straight = False

    low_straight = {"A", "2", "3", "4", "5"}
    if low_straight.issubset(set(check_straight)):
        straight = True
        highest_card = "5"

    if straight and flush:
        return "Straight-Flush", (highest_card)
    elif flush:
        return "Flush", (x for x in check_straight[:5])
    elif straight:
        return "Straight", (highest_card)

    # check for two pair or 3-of-a-kind
    if rank_list[0][1] == 3:
        return "3-of-a-Kind", (rank[0] for rank in rank_list[:3])
    elif rank_list[0][1] == 2 and rank_list[1][1] == 2:
        return "Two-Pair", (rank[0] for rank in rank_list[:3])
    elif rank_list[0][1] == 2:
        return "One-Pair", (rank[0] for rank in rank_list[:4])
    else:
        return "High-Card", (rank[0] for rank in rank_list[:5])
