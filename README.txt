usage: deal-converter.py [-h] INPUT_FILE [OUTPUT_FILE [OUTPUT_FILE ...]]

Universal converter for bridge deal formats

positional arguments:
  INPUT_FILE   Input file path
  OUTPUT_FILE  Output file path(s)

optional arguments:
  -h, --help   show this help message and exit
  --jfr        For PBN file, write only JFR DD fields

Supported formats: BER BHG BRI CDS CSV DGE DLM DUP PBN RZD.
Formats are auto-detected based on file extension.
To display deals on STDOUT, provide "-" as an output file name.
To print deals to HTML file, use *.html output file.
To print deals to PDF file, use *.pdf output file.

PDF output requires wkhtmltopdf in a patched-qt version.

Web interface available: https://deal.emkael.info/
