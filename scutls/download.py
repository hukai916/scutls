import json
import importlib_resources
import wget
import os
from os import path
import cmd
import inspect
import argparse

def download(list_genome_ucsc = False, list_genome_ensembl = False, genome_ucsc = None, genome_ensembl = None, outdir = "./"):
    """download subcommand
    Paramters
    ---------

    list_genome_ucsc : bool
        list all UCSC genome names
    list_genome_ensembl : bool
        list all ENSEMBL genome names
    genome_ucsc : str
        download genome given UCSC genome name
    genome_ensembl : str
        download genome given ENSEMBL genome name
    outdir : str
        output directory, default to "./"
    """

    args = list(locals().keys())
    args.remove("outdir")

    local = locals()
    if all(bool(local[key]) is not True for key in args): # use True since args can be either None or False
        print("scutls download: warning: use 'scutls download -h' for usage")

    resources = importlib_resources.files("scutls")
    dict_genome_ucsc = json.loads((resources / "assets" / "genome_ucsc.json").read_bytes()) # https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package
    dict_genome_ensembl = json.loads((resources / "assets" / "genome_ensembl.json").read_bytes())

    # print available USCS genomes:ing
    if list_genome_ucsc:
        print("Supported UCSC genomes:")
        cli = cmd.Cmd()
        cli.columnize(list(dict_genome_ucsc.keys()), displaywidth=80)

    # print available ENSEMBL genomes:
    if list_genome_ensembl:
        print("Supported ENSEMBL genomes:")
        cli = cmd.Cmd()
        cli.columnize(list(dict_genome_ensembl.keys()), displaywidth=80)

    # download specified UCSC genome:
    if type(genome_ucsc) != type(None):
        if not genome_ucsc in dict_genome_ucsc.keys():
            print("WARNING: " + genome_ucsc + " not supported!")
        else:
            url = dict_genome_ucsc[genome_ucsc]["genome"]
            # filename = wget.download(url)
            print("Downloading " + genome_ucsc + " ...")
            if not os.path.exists(outdir):
                os.mkdir(outdir)
            wget.download(url, out = outdir)
            print("\nDownloaded to " + path.join(outdir, path.basename(url)) + "!")

    # download specified ENSEMBL genome:
    if type(genome_ensembl) != type(None):
        if not genome_ensembl in dict_genome_ensembl.keys():
            print("WARNING: " + genome_ensembl + " not supported!")
        else:
            url = dict_genome_ensembl[genome_ensembl]["genome"]
            print("Downloading " + genome_ensembl + " ...")
            if not os.path.exists(outdir):
                os.mkdir(outdir)
            wget.download(url, out = outdir)
            print("\nDownloaded to " + path.join(outdir, path.basename(url)) + "!")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--list_genome_ucsc', '-lgu', action='store_true')
    parser.add_argument('--list_genome_ensembl', '-lge', action='store_true')
    parser.add_argument('--genome_ucsc', '-gu', type = str)
    parser.add_argument('--genome_ensembl', '-ge', type = str)

    args = parser.parse_args()
    download(args.list_genome_ucsc, args.list_genome_ensembl, args.genome_ucsc, args.genome_ensembl, outdir = "./")

if __name__ == "__main__":
    main()
