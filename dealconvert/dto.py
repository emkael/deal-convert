POSITION_NORTH = 0
POSITION_EAST = 1
POSITION_SOUTH = 2
POSITION_WEST = 3
SUIT_SPADES = 0
SUIT_HEARTS = 1
SUIT_DIAMONDS = 2
SUIT_CLUBS = 3

class Deal(object):
    event = ''
    number = None
    vulnerable = None
    dealer = None
    hands = None

    def __init__(self):
        self.hands = [[[],[],[],[]],
                      [[],[],[],[]],
                      [[],[],[],[]],
                      [[],[],[],[]]]
        self.vulnerable = {'NS': False, 'EW': False}
