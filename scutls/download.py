import json
import importlib_resources
import wget
import os
from os import path

def download(list_genome_ucsc, genome_ucsc, outdir = "./"):
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

    resources = importlib_resources.files("scutls")
    data = (resources / "assets" / "genome_ucsc.json").read_bytes() # https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package
    dict_genome_ucsc = json.loads(data)

    # print available USCS genomes:
    if list_genome_ucsc:
        print("Supported UCSC genomes:")
        for name in dict_genome_ucsc.keys():
            print(name, end = " ")
        print()

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
