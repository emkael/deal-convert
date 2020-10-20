import warnings

from . import BinaryFormat
from .rzd import RZDFormat
from .. import dto

class CDSFormat(BinaryFormat):
    @property
    def suffix(self):
        return '.cds'

    def __init__(self, *args, **kwargs):
        self.rzd_format = RZDFormat()

    def parse_content(self, content):
        dealset = []
        while True:
            data = content.read(14)
            if len(data) < 14:
                if len(data) != 0:
                    warnings.warn('.cds data truncated: %s' % (data))
                break
            deal = dto.Deal()
            deal.number = self.parse_byte(data[0])
            deal.dealer = deal.get_dealer(deal.number)
            deal.vulnerable = deal.get_vulnerability(deal.number)
            deal.hands = self.rzd_format.parse_deal(data[1:], offset=1)
            dealset.append(deal)
        return dealset

    def output_content(self, out_file, dealset):
        for deal in dealset:
            out_file.write(bytearray([deal.number]))
            out_file.write(bytearray(self.rzd_format.dump_deal(deal, offset=1)))
