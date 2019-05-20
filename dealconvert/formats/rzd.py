from . import DealFormat

class RZDFormat(DealFormat):
    @property
    def suffix(self):
        return '.rzd'
