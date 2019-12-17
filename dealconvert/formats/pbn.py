import re, sys, warnings

from bcdd.PBNBoard import PBNBoard
from bcdd.DDTable import DDTable
from bcdd.ParScore import ParScore

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

    def __repr__(self):
        return '[%s "%s"]' % (self.key, self.value) \
            if self.key is not None else self.value

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

    def get_field(self, fieldname, obj=False):
        for field in self.fields:
            if field.key == fieldname:
                return field if obj else field.value
        return None

    def get_optimum_table(self):
        table = []
        found = False
        for field in self.fields:
            if field.key == 'OptimumResultTable':
                table.append(str(field))
                found = True
            else:
                if found:
                    if field.key is None:
                        table.append(str(field))
                    else:
                        break
        return table


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
            if deal_obj.has_field('Dealer'):
                deal_dto.dealer = dealers[deal_obj.get_field('Dealer')]
            else:
                if deal_dto.number is not None:
                    deal_dto.dealer = deal_dto.get_dealer(deal_dto.number)
            if deal_obj.has_field('Vulnerable'):
                vulnerability = deal_obj.get_field('Vulnerable')
                for pair in deal_dto.vulnerable:
                    deal_dto.vulnerable[pair] = vulnerability in [pair, 'All']
            else:
                if deal_dto.number is not None:
                    deal_dto.vulnerable = deal_dto.get_vulnerability(deal_dto.number)
            deal_parts = deal_obj.get_field('Deal').split(':')
            dealer = dealers[deal_parts[0]]
            hands = deal_parts[1].split(' ')
            for hand in range(0, 4):
                for i, suit in enumerate(hands[hand].split('.')):
                    deal_dto.hands[(hand + dealer) % 4][i] = list(suit)
            result.append(deal_dto)
            if deal_obj.has_field('OptimumResultTable'):
                deal_dto.extra_fields += deal_obj.get_optimum_table()
            for field in ['Ability', 'Minimax', 'OptimumScore']:
                if deal_obj.has_field(field):
                    deal_dto.extra_fields.append(
                        str(deal_obj.get_field(field, True)))
        return result

    def output_content(self, out_file, dealset):
        for board in dealset:
            lines = []
            lines.append('[Event "%s"]' % (board.event))
            lines.append('[Board "%d"]' % (board.number))
            lines.append('[Dealer "%s"]' % (
                'NESW'[board.dealer]
            ))
            lines.append('[Vulnerable "%s"]' % (
                ('All' if board.vulnerable['EW'] else 'NS') if
                board.vulnerable['NS'] else
                ('EW' if board.vulnerable['EW'] else 'None')
            ))
            lines.append('[Deal "N:%s"]' % (
                ' '.join([
                    '.'.join([''.join(suit) for suit in hand])
                    for hand in board.hands
                ])))
            for field in board.extra_fields:
                lines.append(field)
            if self.analyze:
                try:
                    dd_board = PBNBoard(lines)
                    dd_table = DDTable(dd_board).get_dd_table(self.interactive)
                    dd_contract = ParScore(dd_board).get_par_contract(dd_table)
                    dd_board.save_dd_table(dd_table, jfr_only=self.options.get('jfr_only', False))
                    dd_board.save_par_contract(dd_contract, jfr_only=self.options.get('jfr_only', False))
                    lines = [field.raw_field for field in dd_board.fields]
                except Exception as e:
                    warnings.warn('unable to determine double-dummy data: %s' % e)
            for line in lines + ['']:
                out_file.write(line + '\r\n')
