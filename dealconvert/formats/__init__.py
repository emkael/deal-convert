from os.path import dirname, basename, isfile, join
import glob

class DealFormat(object):
    cards = 'AKQJT98765432'

    def __init__(self, interactive=True, jfr_only=False):
        self.interactive = interactive
        self.jfr_only = jfr_only

    def parse(self, input_file):
        with open(input_file, 'rb') as content:
            return self.parse_content(content)

    def output(self, output_file, deal, analyze=False):
        self.analyze = analyze
        if not len(deal):
            raise RuntimeError('Dealset is empty')
        with open(output_file, 'wb') as out_file:
            return self.output_content(out_file, deal)

    def match_file(self, filename):
        return filename.lower().endswith(self.suffix)

    @property
    def suffix(self):
        pass

    def parse_content(self, content):
        pass

    def output_content(self, out_file, deal):
        pass


modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [
    basename(f)[:-3] for f in modules
    if isfile(f) and not f.endswith('__init__.py')
]
