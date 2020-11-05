from importlib import import_module


class DealConverter(object):
    def __init__(self, input_file=None, **kwargs):
        self.input = input_file
        self.formats = {}
        self.format_options = kwargs
        if input_file is not None:
            self.parser = self.detect_format(self.input)

    def output(self, output_files):
        deal_set = sorted(self.parser.parse(self.input), key=lambda d:d.number)
        for output in output_files:
            self.detect_format(output).output(output, deal_set, True)

    def detect_format(self, filename, interactive=True):
        for deal_format in import_module('.formats', 'dealconvert').__all__:
            if deal_format not in self.formats:
                mod = import_module('.formats.' + deal_format, 'dealconvert')
                self.formats[deal_format] = getattr(
                    mod,
                    deal_format.upper() + 'Format')(interactive, **self.format_options)
            if self.formats[deal_format].match_file(filename):
                return self.formats[deal_format]
        raise RuntimeError('Unrecognized file extension: %s' % filename)
