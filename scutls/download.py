import json
import importlib_resources
import wget
import os
from os import path
import cmd

def download(list_genome_ucsc, list_genome_ensembl, genome_ucsc, genome_ensembl, outdir = "./"):
    """Download utilities
    Paramters
    ---------
    flag : str
        What to perform:
            genome_ucsc : download genome given UCSC genome name
            list_genome_ucsc : list all available UCSC genome names
            genome_ensembl : download genome given ENSEMBL genome name
    outdir : str
        Output directory
    """

    if (not list_genome_ucsc and not list_genome_ensembl and not genome_ucsc and not genome_ensembl):
        print("Try: scutls download -h")

    resources = importlib_resources.files("scutls")
    dict_genome_ucsc = json.loads((resources / "assets" / "genome_ucsc.json").read_bytes()) # https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package
    dict_genome_ensembl = json.loads((resources / "assets" / "genome_ensembl.json").read_bytes())

    # print available USCS genomes:
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
