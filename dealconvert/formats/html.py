from collections import OrderedDict
import warnings

from bcdd.BCalcWrapper import BCalcWrapper
from bcdd.DDTable import DDTable
from bcdd.Exceptions import FieldNotFoundException
from bcdd.ParScore import ParScore
from bcdd.PBNBoard import PBNBoard

from . import DealFormat
from .. import dto


HTML_SUITS = OrderedDict([
    ('s', u'\u2660'),
    ('h', u'\u2665'),
    ('d', u'\u2666'),
    ('c', u'\u2663')
])

_page_template = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style type="text/css">
table {
    border-collapse: collapse;
    table-layout: fixed;
    page-break-inside:avoid;
    font-size: 8pt;
    font-family: Arial, "Sans-serif";
}
@media screen {
    table {
        font-size: 12px;
    }
    thead {
        display: table-header-group;
    }
}
tr {
    page-break-inside:avoid;
    page-break-after:auto;
}
td {
    page-break-inside:avoid;
    overflow: visible;
    padding-bottom: 0;
}
thead {
    font-size: 10pt;
    text-align: left;
    display: none;
}
.suit-d, .suit-h {
    color: red;
}
</style>
</head>
<body>
<table width="100%%">
<thead>
<tr>
<th colspan="%d">%s</th>
</tr>
</thead>
</table>
%s
</body>
</html>
'''

class HTMLFormat(DealFormat):
    @property
    def suffix(self):
        return '.html'

    def __init__(self, *args, **kwargs):
        DealFormat.__init__(self, *args, **kwargs)
        self.deals_per_column = self.options.get('columns', 6) or 6

    def parse_content(self, content):
        raise NotImplementedError

    def _get_html_hands(self, deal):
        suits = HTML_SUITS.keys()
        return [
            [
                self._get_html_suit(suits[i], suit)
                for i, suit in enumerate(hand)
            ] for hand in deal.hands
        ]

    def _get_suit_symbol(self, suit):
        return '<span class="suit-%s">%s</span>' % (
            suit, HTML_SUITS[suit]
        )

    def _get_html_suit(self, suit, cards):
        return '&nbsp;%s&nbsp;%s' % (
            self._get_suit_symbol(suit), ''.join(cards).replace('T', '10'))

    def _get_deal_header(self, board):
        try:
            conditions = '%s / %s' % (
                'NESW'[board.dealer],
                ('all' if board.vulnerable['EW'] else 'NS') if
                board.vulnerable['NS'] else
                ('EW' if board.vulnerable['EW'] else 'none')
            )
        except:
            conditions = ''
        return '<div style="width:100%; text-align: center; font-size: 0.5rem">' + \
            '<span style="font-size: 1.5rem">' + \
            str(board.number) + \
            '</span><br />' + \
            conditions + \
            '</div>'

    def _get_dd_data(self, board):
        data = {
            'par': '',
            'table': ''
        }

        pbn_board = PBNBoard(board.extra_fields)

        dd_table = DDTable(pbn_board)
        tricks_table = None
        try:
            tricks_table = dd_table.get_pbn_table()
        except FieldNotFoundException:
            try:
                tricks_table = dd_table.get_jfr_table()
            except FieldNotFoundException:
                pass
        if tricks_table is not None:
            data['table'] = '<table style="font-size: 0.5rem; width: 100%">'
            data['table'] += '<tr style="border-bottom: solid 1px black"><td>&nbsp;</td><td>nt</td>'
            for suit in 'shdc':
                data['table'] += '<td>' + self._get_suit_symbol(suit) + '</td>'
            data['table'] += '</tr>'
            player_order = [0, 2, 1, 3] # NESW -> NSEW
            denom_order = range(4, -1, -1) # CDHSN -> NSHDC
            for player in player_order:
                data['table'] += '<tr>'
                data['table'] += '<td style="border-left: solid 1px black">' + BCalcWrapper.PLAYERS[player] + '</td>'
                for denom in denom_order:
                    data['table'] += '<td>'
                    data['table'] += str(tricks_table[player][denom] - 6) if tricks_table[player][denom] > 6 else '&nbsp;'
                    data['table'] += '</td>'
                data['table'] += '</tr>'
            data['table'] += '</table>'

        par_score = ParScore(pbn_board)
        par_contract = None
        try:
            par_contract = par_score.get_pbn_par_contract()
        except FieldNotFoundException:
            try:
                par_contract = par_score.get_jfr_par_contract()
            except FieldNotFoundException:
                pass
        if par_contract is not None:
            data['par'] = '<span style="font-size: 0.6rem">Minimax:<br />%d%s%s&nbsp;%s&nbsp;%+d</span>' % (
                par_contract.level,
                'NT' if par_contract.denomination == 'N' \
                else self._get_suit_symbol(par_contract.denomination.lower()),
                'x' if par_contract.doubled else '',
                par_contract.declarer,
                par_contract.score)
        return data

    def _get_table_directions(self):
        return '<table width="100%" style="text-align: center">' + \
            '<tr><td>&nbsp;</td><td>N</td><td>&nbsp;</td></tr>' + \
            '<tr><td>W</td><td>&nbsp;</td><td>E</td></tr>' + \
            '<tr><td>&nbsp;</td><td>S</td><td>&nbsp;</td></tr>' + \
            '</table>'

    def get_html_content(self, dealset):
        deal_rows = []
        event_name = dealset[0].event
        while len(dealset) > 0:
            deal_rows.append(dealset[0:self.deals_per_column])
            dealset = dealset[self.deals_per_column:]
        table_content = ''
        for row in deal_rows:
            table_content += '<table style="margin-top: -1px"><tr>'
            for deal in row:
                table_content += '<td style="width: 6.4cm; border: solid 1px black; padding: 0">'
                deal_cells = [
                    ['', '', '', ''],
                    ['', '', '', ''],
                    ['', '', '', ''],
                ]
                hands = self._get_html_hands(deal)
                dd_data = self._get_dd_data(deal)
                deal_cells[0][1] = '<br />'.join(hands[0])
                deal_cells[0][3] = self._get_deal_header(deal)
                deal_cells[1][0] = '<br />'.join(hands[3])
                deal_cells[1][1] = self._get_table_directions()
                deal_cells[1][2] = '<br />'.join(hands[1])
                deal_cells[2][0] = dd_data['par']
                deal_cells[2][1] = '<br />'.join(hands[2])
                deal_cells[2][3] = dd_data['table']
                deal_content = '<table width="100%">'
                for deal_row in deal_cells:
                    deal_content += '<tr>'
                    for idx, deal_cell in enumerate(deal_row):
                        deal_content += '<td width="%d%%">' % [30, 20, 20, 30][idx]
                        deal_content += deal_cell
                        deal_content += '</td>'
                    deal_content += '</tr>'
                deal_content += '</table>'
                table_content += deal_content
                table_content += '</td>'
            table_content += '</tr></table>'
        return _page_template % (
            self.deals_per_column, event_name, table_content
        )

    def output_content(self, out_file, dealset):
        out_file.write(self.get_html_content(dealset).encode('utf-8'))
