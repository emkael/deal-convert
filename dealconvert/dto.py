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
    extra_fields = None

    def __init__(self):
        self.hands = [[[],[],[],[]],
                      [[],[],[],[]],
                      [[],[],[],[]],
                      [[],[],[],[]]]
        self.vulnerable = {'NS': False, 'EW': False}
        self.extra_fields = []

    def get_dealer(self, board_no):
        return (board_no - 1) % 4

    def get_vulnerability(self, board_no):
        board_no = board_no % 16
        vuln = {'NS': [False,
                       False, True, False, True,
                       True, False, True, False,
                       False, True, False, True,
                       True, False, True],
                'EW': [True,
                       False, False, True, True,
                       False, True, True, False,
                       True, True, False, False,
                       True, False, False]}
        return { pair: vuln[pair][board_no] for pair in vuln }

    def fill_west(self):
        for suit in range(0, 4):
            for card in 'AKQJT98765432':
                if card not in self.hands[0][suit] + self.hands[1][suit] + self.hands[2][suit]:
                    self.hands[3][suit].append(card)
