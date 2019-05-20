from . import DealFormat

class CSVFormat(DealFormat):
    @property
    def suffix(self):
        return '.csv'
