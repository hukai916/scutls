import sys
from argparse import ArgumentParser
from scutls import cli

parser = ArgumentParser(description = "Single-cell sequencing utility tools")
subparsers = parser.add_subparsers(title = "Subcommands")

# download
parser_download = subparsers.add_parser(
    "download", description = "download genome/annotation file from UCSC/ENSEMBL")
parser_download.add_argument(
    "-o", "--outdir",
    help = "output directory, default to ./",
    required = False, type = str, default = "./"
)
parser_download.add_argument(
    "-lgu",
    "--list_genome_ucsc",
    help="list all available UCSC genome names",
    required = False,
    action='store_true' # quick hack to skip requred input: https://stackoverflow.com/questions/59363298/argparse-expected-one-argument
)
parser_download.add_argument(
    "-gu",
    "--genome_ucsc",
    help="a UCSC genome name to download",
    required = False,
    type = str
)
parser_download.add_argument(
    "-lge",
    "--list_genome_ensembl",
    help="list all available ENSEMBL genome names",
    required = False,
    action='store_true' # quick hack to skip requred input: https://stackoverflow.com/questions/59363298/argparse-expected-one-argument
)
parser_download.add_argument(
    "-ge",
    "--genome_ensembl",
    help="an ENSEMBL genome name to download",
    required = False,
    type = str
)
parser_download.set_defaults(func=cli.run_download)

def main():
    if len(sys.argv[1:]) == 0:
        parser.print_help()
        parser.exit()
    else:
        args = parser.parse_args()
        # sys.setrecursionlimit(200000)
        args.func(args) # parse the args and call whatever function was selected

if __name__ == "__main__":
    main()
