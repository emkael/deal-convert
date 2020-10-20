from os.path import dirname, basename, isfile, join
import glob

class DealFormat(object):
    cards = 'AKQJT98765432'

    def __init__(self, interactive=True, **kwargs):
        self.interactive = interactive
        self.options = kwargs

    def file_to_read(self, input_path):
        return open(input_path, 'r')

    def file_to_write(self, output_path):
        return open(output_path, 'w')

    def parse(self, input_file):
        with self.file_to_read(input_file) as content:
            return self.parse_content(content)

    def output(self, output_file, deal, analyze=False):
        self.analyze = analyze
        if not len(deal):
            raise RuntimeError('Dealset is empty')
        with self.file_to_write(output_file) as out_file:
            return self.output_content(out_file, deal)

    def match_file(self, filename):
        return filename.lower().endswith(self.suffix)

    def parse_byte(self, byte):
        try:
            converted_byte = ord(byte)
            byte = converted_byte
        except TypeError:
            converted_byte = byte # in Python3, ord() is not needed
        return converted_byte

    @property
    def suffix(self):
        pass

    def parse_content(self, content):
        pass

    def output_content(self, out_file, deal):
        pass


class BinaryFormat(DealFormat):
    def file_to_read(self, input_path):
        return open(input_path, 'rb')

    def file_to_write(self, output_path):
        return open(output_path, 'wb')


modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [
    basename(f)[:-3] for f in modules
    if isfile(f) and not f.endswith('__init__.py')
]
