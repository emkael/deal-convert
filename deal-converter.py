import argparse, sys

from dealconvert import DealConverter

converter = DealConverter(sys.argv[1])
converter.output(sys.argv[2:])
