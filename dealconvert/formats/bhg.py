from . import DealFormat

class BHGFormat(DealFormat):
    @property
    def suffix(self):
        return '.bhg'
