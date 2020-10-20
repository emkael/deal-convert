import filecmp, itertools, os, sys, tempfile

pybcddpath = os.path.realpath(os.path.join(os.path.dirname(__file__), 'pybcdd'))
sys.path.append(pybcddpath)

from dealconvert import DealConverter

import pytest


formats = ['ber', 'bhg', 'bri', 'rzd', 'cds', 'csv', 'dge', 'dlm', 'dup', 'lin', 'pbn']
format_files = ['test.' + f for f in formats] + ['test-jfr.pbn']
test_data = [(d[0], d[1], d[1] == 'test-jfr.pbn') for d in itertools.product(format_files, format_files)]


@pytest.mark.parametrize("input_file, output_file, jfr_only", test_data)
def test_conversion(input_file, output_file, jfr_only):
    input_path = os.path.join(os.path.dirname(__file__), 'test', input_file)
    output_path = os.path.join(os.path.dirname(__file__), 'test', 'tmp', output_file)
    ref_path = os.path.join(os.path.dirname(__file__), 'test', output_file)
    if os.path.exists(output_path):
        os.remove(output_path)
    converter = DealConverter(
        input_path,
        jfr_only=jfr_only)
    converter.output([output_path])
    assert filecmp.cmp(output_path, ref_path)
