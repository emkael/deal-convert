import tempfile
import warnings

import pdfkit

from . import DealFormat
from .html import HTMLFormat
from .. import dto


class PDFFormat(DealFormat):
    @property
    def suffix(self):
        return '.pdf'

    def __init__(self, *args, **kwargs):
        DealFormat.__init__(self, *args, **kwargs)
        self.html_formatter = HTMLFormat(*args, **kwargs)

    def parse_content(self, content):
        raise NotImplementedError

    def output_content(self, out_file, dealset):
        html_content = self.html_formatter.get_html_content(dealset)
        temp_file = tempfile.NamedTemporaryFile(delete=True)
        pdfkit.from_string(html_content, temp_file.name, options={
            'quiet': '',
            'margin-bottom': '0',
            'margin-top': '0.35cm',
            'margin-left': '0',
            'margin-right': '0',
            'print-media-type': '',
            'page-size': 'A4',
            'header-left': '   ' + dealset[0].event,
            'header-right': 'Page [page]   ',
            'header-font-size': '8',
            'orientation': self.options.get('orientation', 'Landscape') or 'Landscape'
        })
        out_file.write(temp_file.read())
        temp_file.close()
