from . import DealFormat

class DLMFormat(DealFormat):
    @property
    def suffix(self):
        return '.dlm'
