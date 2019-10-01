from __future__ import print_function
import argparse, os, sys, warnings

pybcddpath = os.path.realpath(os.path.join(os.path.dirname(__file__), 'pybcdd'))
sys.path.append(pybcddpath)

from dealconvert import DealConverter

parser = argparse.ArgumentParser(
    description='Universal converter for bridge deal formats',
    formatter_class=argparse.RawTextHelpFormatter,
    epilog='Supported formats: BER BHG BRI CDS CSV DGE DLM DUP PBN RZD.\n' + \
    'Formats are auto-detected based on file extension.\n' + \
    'To display deals on STDOUT, provide "-" as an output file name.')
parser.add_argument('--jfr', action='store_true',
                    help='For PBN file, write only JFR DD fields')
parser.add_argument('input', metavar='INPUT_FILE',
                    help='Input file path')
parser.add_argument('output', metavar='OUTPUT_FILE', nargs='*',
                    help='Output file path(s)')

arguments = parser.parse_args()

def _warning(msg, *args, **kwargs):
    print('WARNING: %s' % (msg), file=sys.stderr)
warnings.showwarning = _warning

try:
    converter = DealConverter(arguments.input, jfr_only=arguments.jfr)
    converter.output(arguments.output)
except RuntimeError as e:
    print('ERROR: %s' % (str(e)), file=sys.stderr)
