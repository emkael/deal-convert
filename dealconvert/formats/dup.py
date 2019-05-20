from . import DealFormat

class DUPFormat(DealFormat):
    @property
    def suffix(self):
        return '.dup'
