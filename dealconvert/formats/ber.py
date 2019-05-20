from . import DealFormat

class BERFormat(DealFormat):
    @property
    def suffix(self):
        return '.ber'
