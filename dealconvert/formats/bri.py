from . import DealFormat

class BRIFormat(DealFormat):
    @property
    def suffix(self):
        return '.bri'
