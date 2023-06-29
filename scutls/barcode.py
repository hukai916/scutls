import argparse
import functools
from multiprocessing import Pool
from Bio import SeqIO, bgzf
from Bio.Seq import Seq
from .util import fastq_chunk_interval, fastq_contain_barcode, get_search_pattern, fastq_locate_barcode, special_search_character
import os
import regex

def barcode(input = None, output = None, output2 = None, contain = None, locate = None, pos = 0, error = 1, mismatch_only = False, rc_barcode = False, nproc = 1):
    """barcode subcommand
    Paramters
    ---------

    input : str
        input file name, auto detects .gz
    output : str
        output file name, auto detects .gz, contains fastq that contains specified barcode via contain
    contain: str
        barcode to detect, if multiple barcodess, separate with comma: "AATTCCC,AGGGCCC,CCGGCG", if pattern contains special characters including "()", "{}", "*", "=", the pattern will be passed as searching pattern
        # optional for "contain" sub-command:
        error: int
            allowed nucleotide mismatches (can be INDELs) when searching regex pattern, default to 1
        mismatch_only: bool
            if true, only mismatches (INDELs excluded) are allowed when searching regex pattern, default to False
        nproc: int
            number of parallel jobs, default to 1
        rc_barcode: bool
            take reverse complement of the barcode when aligning, default to False
    locate: str
        barcode to detect its location in reads
        # shared arguments with "contain": error, mismatch_only, nproc, rc_barcode
        pos: int
            which matched position to return, default to 0 meaning the first, use -1 to indicate the last.
        
    """

    args = list(locals().keys())

    local = locals()
    if all(bool(local[key]) is not True for key in args): 
        print("scutls fastq: warning: use 'scutls contain -h' for usage")
    # use True since args can be either None or False
    # arguments.py defines requirments of each argument

    # check if input fastq contains specified barcode:
    if contain:
        # prepare search pattern
        for character in special_search_character:
            if character in contain:
                barcode_pattern = contain 
                break
            else:
                barcode_pattern = get_search_pattern(pattern = contain, error = error, mismatch_only = mismatch_only, rc_barcode = rc_barcode)
        
        # print("barcode_pattern: ", barcode_pattern)

        # multiprocessing
        if not output == None:
            print("Saving to " + output + " ...")
        else:
            print("Processing ...")
        intervals = fastq_chunk_interval(input, nproc = nproc)
        p = Pool(nproc)
        res = p.map_async(
            functools.partial(
                fastq_contain_barcode,
                fastq = input,
                barcode_pattern = barcode_pattern),
                intervals.values()).get()
        fastq_hit, fastq_non_hit = [], []
        
        for x in range(len(res)):
            fastq_hit = fastq_hit + [hit for hit in res[x][0]]
            fastq_non_hit = fastq_non_hit + [non_hit for non_hit in res[x][1]]

        if not output == None:
            if not os.path.dirname(output) == "":
                os.makedirs(os.path.dirname(output), exist_ok=True)
            if output.endswith(".gz"):
                with bgzf.BgzfWriter(output, "wb") as outgz:
                    SeqIO.write(sequences = fastq_hit, handle = outgz, format="fastq")
            else:
                SeqIO.write(fastq_hit, output, "fastq")
        else:
            for record in fastq_hit:
                print(record.seq, [x.start() for x in regex.finditer(barcode_pattern, str(record.seq))])
        
        if not output2 == None:
            print("Saving to " + output2 + " ...")
            if not os.path.dirname(output2) == "":
                os.makedirs(os.path.dirname(output2), exist_ok=True)
            if output2.endswith(".gz"):
                with bgzf.BgzfWriter(output2, "wb") as outgz:
                    SeqIO.write(sequences = fastq_non_hit, handle = outgz, format="fastq")
            else:
                SeqIO.write(fastq_non_hit, output2, "fastq")
        
        print("Done!")

    # check if input fastq contains specified barcode
    if locate:
        # prepare search pattern
        for character in special_search_character:
            if character in locate:
                barcode_pattern = locate 
                break
        else:
            barcode_pattern = get_search_pattern(pattern = locate, error = error, mismatch_only = mismatch_only, rc_barcode = rc_barcode)

        # multiprocessing
        intervals = fastq_chunk_interval(input, nproc = nproc)
        p = Pool(nproc)
        res_list = p.map_async(
            functools.partial(
                fastq_locate_barcode,
                fastq = input,
                barcode_pattern = barcode_pattern,
                pos = pos),
                intervals.values()).get()
        for res in res_list:
            for res_items in res:
                print(res_items[0], res_items[1], res_items[2])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',  '-i', type   = str)
    parser.add_argument('--output', '-o', type   = str)
    parser.add_argument('--output2', '-o2', type = str)
    parser.add_argument('--contain', '-c', type = str)
    parser.add_argument('--locate', '-l', type = str)
    parser.add_argument('--position', '-p', type = int)
    
    parser.add_argument('--error',   '-e', type   = int)
    parser.add_argument('--mismatch_only', '-m', default = False)
    parser.add_argument('--rc_barcode', '-rcb', default = False)
    parser.add_argument('--num_processor', '-nproc', default = 1)
    
if __name__ == "__main__":
    main()
