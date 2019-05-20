import re

from . import DealFormat
from .. import dto

class PBNField(object):
    __slots__ = ['key', 'value']
    def __init__(self, key, value):
        self.key = key
        self.value = value

    field_regex = re.compile(r'\[(.*) "(.*)"\]')

    @staticmethod
    def parse_line(line):
        match = PBNField.field_regex.match(line)
        if match:
            return PBNField(key=match.group(1), value=match.group(2))
        return PBNField(None, line)

class PBNDeal(object):
    __slots__ = ['fields']

    def parse(self, lines):
        self.fields = []
        for line in lines:
            self.fields.append(PBNField.parse_line(line))

    def has_field(self, fieldname):
        for field in self.fields:
            if field.key == fieldname:
                return True
        return False

    def get_field(self, fieldname):
        for field in self.fields:
            if field.key == fieldname:
                return field.value
        return None

class PBNFormat(DealFormat):
    @property
    def suffix(self):
        return '.pbn'

    def parse_content(self, content):
        lines = [line.strip() for line in content.readlines()]
        deals = []
        current_deal = []
        for line in lines:
            if len(line):
                current_deal.append(line)
            else:
                deals.append(current_deal)
                current_deal = []
        if len(current_deal):
            deals.append(current_deal)
        result = []
        for deal in deals:
            deal_obj = PBNDeal()
            deal_obj.parse(deal)
            deal_dto = dto.Deal()
            if deal_obj.has_field('Event'):
                deal_dto.event = deal_obj.get_field('Event')
            if deal_obj.has_field('Board'):
                deal_dto.number = int(deal_obj.get_field('Board'))
            dealers = {'N': dto.POSITION_NORTH,
                       'E': dto.POSITION_EAST,
                       'S': dto.POSITION_SOUTH,
                       'W': dto.POSITION_WEST}
            deal_dto.dealer = dealers[deal_obj.get_field('Dealer')]
            vulnerability = deal_obj.get_field('Vulnerable')
            for pair in deal_dto.vulnerable:
                deal_dto.vulnerable[pair] = vulnerability in [pair, 'All']
            deal_parts = deal_obj.get_field('Deal').split(':')
            dealer = dealers[deal_parts[0]]
            hands = deal_parts[1].split(' ')
            for hand in range(0, 4):
                for i, suit in enumerate(hands[hand].split('.')):
                    deal_dto.hands[(hand + dealer) % 4][i] = list(suit)
            result.append(deal_dto)
        return result

    def output_content(self, out_file, deal):
        for board in deal:
            out_file.write('[Event "%s"]\r\n' % (board.event))
            out_file.write('[Board "%d"]\r\n' % (board.number))
            out_file.write('[Dealer "%s"]\r\n' % (
                'NESW'[board.dealer]
            ))
            out_file.write('[Vulnerable "%s"]\r\n' % (
                ('All' if board.vulnerable['EW'] else 'NS') if
                board.vulnerable['NS'] else
                ('EW' if board.vulnerable['EW'] else 'None')
            ))
            out_file.write('[Deal "N:%s"]\r\n' % (
                ' '.join([
                    '.'.join([''.join(suit) for suit in hand])
                    for hand in board.hands
                ])))
            out_file.write('\r\n')
