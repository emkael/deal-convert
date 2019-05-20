from . import DealFormat

class CDSFormat(DealFormat):
    @property
    def suffix(self):
        return '.cds'
