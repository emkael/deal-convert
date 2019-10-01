import warnings

from . import DealFormat
from .bri import BRIFormat
from .dge import DGEFormat
from .. import dto

class DUPFormat(DealFormat):
    @property
    def suffix(self):
        return '.dup'

    def __init__(self, *args, **kwargs):
        self.bri = BRIFormat()
        self.dge = DGEFormat()

    def parse_content(self, content):
        boards = []
        while True:
            boards.append(content.read(156))
            if len(boards[-1]) < 156:
                if len(boards[-1]) > 0:
                    warnings.warn('truncated .dup content: %s' % (boards[-1]))
                boards = boards[0:-1]
                break
        boards = [(board[0:78], board[78:146], board[146:]) for board in boards]
        if boards[0][2][0] == chr(0):
            raise RuntimeError('.dup file header not found')
        start_board = int(boards[0][2][2:4].strip())
        board_count = int(boards[0][2][7:9].strip())
        board_numbers = range(start_board, start_board+board_count)
        if boards[0][2][1].upper() != 'N':
            warnings.warn(
                '.dup file header has "reverse" flag set, ' +
                'nobody knows what to do with it, so it\'s time to panic')
        dealset = []
        for idx, board in enumerate(boards):
            deal = dto.Deal()
            deal.number = board_numbers[idx]
            deal.dealer = deal.get_dealer(deal.number)
            deal.vulnerable = deal.get_vulnerability(deal.number)
            deal.hands = self.bri.parse_hands(board[0])
            dealset.append(deal)
        return dealset

    def output_content(self, out_file, dealset):
        board_numbers = [deal.number for deal in dealset]
        first_board = min(board_numbers)
        board_count = len(dealset)
        for board in range(first_board, first_board+board_count):
            if board not in board_numbers:
                raise RuntimeError(
                    '.dup format requires consequent board numbers')
        header = 'YN%s 0 %02d ' % (str(first_board).ljust(2, ' '), board_count)
        for deal in dealset:
            out_file.write(self.bri.single_deal_output(deal))
            out_file.write(self.dge.single_deal_output(deal))
            if deal.number == first_board:
                out_file.write(header)
            else:
                out_file.write(chr(0) * 10)
