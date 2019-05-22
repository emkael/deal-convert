import argparse, sys

from dealconvert import DealConverter

parser = argparse.ArgumentParser(
    description='Universal converter for bridge deal formats',
    formatter_class=argparse.RawTextHelpFormatter,
    epilog='Supported formats: BER BHG BRI CDS CSV DGE DLM DUP PBN RZD.\n' + \
    'Formats are auto-detected based on file extension.')
parser.add_argument('input', metavar='INPUT_FILE',
                    help='Input file path')
parser.add_argument('output', metavar='OUTPUT_FILE', nargs='*',
                    help='Output file path(s)')

arguments = parser.parse_args()

converter = DealConverter(arguments.input)
converter.output(arguments.output)
