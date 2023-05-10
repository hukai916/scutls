import json
import importlib_resources
import wget
import os
from os import path
import cmd
import argparse
from .util import update_ensembl_release, get_ensembl_url_json

def download(list_genome_ucsc = False, list_genome_ensembl = False, genome_ucsc = None, genome_ensembl = None, annotation_ucsc = None, annotation_ensembl = None, ensembl_release = False, ensembl_release_use = None, ensembl_release_update = False, outdir = "./"):
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
    annotation_ucsc : str
        download annotation file given UCSC genome name
    annotation_ensembl : str
        download annotation file given ENSEMBL genome name
    ensembl_release : bool
        list all ENSEMBL releases and the one in use
    ensembl_release_use : str
        update ENSEMBL release in use, input 4 release numbers separated by comma (vertebrates, plants, fungi, metazoa), e.g. -eru '104, 51, 51, 51'
    ensembl_release_update : bool
        update genome_ensembl_release_all.txt

    """

    args = list(locals().keys())
    args.remove("outdir")

    local = locals()
    if all(bool(local[key]) is not True for key in args): # use True since args can be either None or False
        print("scutls download: warning: use 'scutls download -h' for usage")

    resources = importlib_resources.files("scutls")

    # update ensembl_release_all.txt file
    if ensembl_release_update:
        try:
            print("Updating releases in cache ...")
            update_ensembl_release()
            print("Done! Use --ensembl_release to see full list.")
        except:
            print("Updating failed! Pls try again later!")

    # update ensembl_release_use:
    if not ensembl_release_use == None:
        try:
            with open(resources / "assets" / "genome_ensembl_release_use.txt", "w") as f:
                _tem = [x.strip() for x in ensembl_release_use.split(",")]
                assert len(_tem) == 4, "Must provide 4 release numbers!"
                f.write("vertebrates: " + _tem[0] + "\n")
                f.write("plants: " + _tem[1] + "\n")
                f.write("fungi: " + _tem[2] + "\n")
                f.write("metazoa: " + _tem[3] + "\n")
                print("ENSEMBL release in use updated to: " + ",".join(_tem) + "!")
        except:
            print("Updating failed! Check out the correct input format!")

    dict_genome_ucsc = json.loads((resources / "assets" / "genome_ucsc.json").read_bytes()) # https://stackoverflow.com/questions/6028000/how-to-read-a-static-file-from-inside-a-python-package

    with open(resources / "assets" / "genome_ensembl_release_use.txt") as f:
        ensembl_release_current = {}
        for line in f:
            key, value = line.split(": ")
            ensembl_release_current[key] = value.strip()
    with open(resources / "assets" / "genome_ensembl_release_all.txt") as f:
        ensembl_release_all = {}
        for line in f:
            key, values = line.split(": ")
            ensembl_release_all[key] = values
    _tem = "genome_ensembl_" + "_".join(ensembl_release_current.values()) + ".json"

    # print all ensembl releases and the one in use:
    if ensembl_release:
        _tem = ", ".join(ensembl_release_all)
        print("All ENSEMBL releases: ")
        for key in ensembl_release_all:
            print("\t", key, ":", ensembl_release_all[key], end = "")
        print("\nENSEMBL relsease in use: ")
        for key in ensembl_release_current:
            print("\t", key, ":", ensembl_release_current[key], end = "\n")

    try:
        _tem_current = "_".join(["genome_ensembl", *list(ensembl_release_current.values())]) + ".json"
        dict_genome_ensembl = json.loads((resources / "assets" / _tem_current).read_bytes())
    except:
        print("ENSEMBL release " + ",".join(ensembl_release_current.values()) + " not in cache!")
        print("Creating caching file ... may take several minutes ...")
        try:
            get_ensembl_url_json(*list(ensembl_release_current.values()))
            print("Success!")
        except:
            print("Failed! Please try again later")

    # print available UCSC genomes:
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

    # download specified UCSC annotation file:
    if type(annotation_ucsc) != type(None):
        if not annotation_ucsc in dict_genome_ucsc.keys():
            print("WARNING: " + annotation_ucsc + " not supported!")
        else:
            url = dict_genome_ucsc[annotation_ucsc]["gtf"]
            print("Downloading annotation file: " + annotation_ucsc + " ...")
            if not os.path.exists(outdir):
                os.mkdir(outdir)
            wget.download(url, out = outdir)
            print("\nDownloaded to " + path.join(outdir, path.basename(url)) + "!")

    # download specified ENSEMBL annotation file:
    if type(annotation_ensembl) != type(None):
        if not annotation_ensembl in dict_genome_ensembl.keys():
            print("WARNING: " + annotation_ensembl + " not supported!")
        else:
            url = dict_genome_ensembl[annotation_ensembl]["gtf"]
            print("Downloading annotatiion file: " + annotation_ensembl + " ...")
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
