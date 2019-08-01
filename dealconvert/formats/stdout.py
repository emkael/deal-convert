from __future__ import print_function

from . import DealFormat

class STDOUTFormat(DealFormat):
    def match_file(self, filename):
        return filename == '-'

    def parse(self, input_file):
        return []

    def output(self, output_file, deal, analyze=False):
        width = 9
        for board in deal:
            lines = []
            header = '%3d/%s' % (
                board.number,
                ('All' if board.vulnerable['NS'] else 'EW') \
                if board.vulnerable['EW'] else \
                ('NS' if board.vulnerable['NS'] else '-'))
            for suit in board.hands[0]:
                suit = ''.join(suit) if len(suit) else '=='
                lines.append(' ' * width + suit)
            for idx, suit in enumerate(board.hands[3]):
                suit = ''.join(suit) if len(suit) else '=='
                suit = ('%-' + str(width) + 's') % (suit)
                east_suit = ''.join(board.hands[1][idx]) \
                    if len(board.hands[1][idx]) else '=='
                lines.append(suit + ' ' * width + east_suit)
            for suit in board.hands[2]:
                suit = ''.join(suit) if len(suit) else '=='
                lines.append(' ' * width + suit)
            lines.append('')
            lines[1] = header + lines[1][len(header):]
            print('\n'.join(lines))
