from . import DealFormat

class DGEFormat(DealFormat):
    @property
    def suffix(self):
        return '.dge'
