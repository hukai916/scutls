import argparse
from multiprocessing import Pool
import functools
from .util import bam_chunk_interval, bam_locate_pos_in_read, bam_locate_pos_in_ref

def bam(input = None, output = None, locate_pos_in_read = None, locate_pos_in_ref = False, nproc = 1):
    """bam subcommand
    Paramters
    ---------

    input : str
        input file name, must end with .bam
    output : str
        output file name
    locate_pos_in_read : int
        a reference coornidate to be located in each read in the bam file
        ------------------
        Ref:    AATCCGGC
        Query:  AA  CGGC
        Q-pos:  12  3456
        ------------------
        For the above case, if trying to locate reference coordinate 2 (0-based), which is "T", the query pos 2 will be returned. 
    locate_pos_in_ref : bool
        for each read in bam: for every cigar tuple, output the corresponding reference coordinate
    
    nproc : int
        number of parallel jobs, default to 1
        funtions that support nproc: locate_pos_in_read

    """
    args = list(locals().keys())

    local = locals()
    if all(bool(local[key]) is not True for key in args): # use True since args can be either None or False
        print("scutls bam: warning: use 'scutls bam -h' for usage")

    # locate a given reference coordinate in each read
    if locate_pos_in_read:
        if output == None:
            pass
        else:
            print("Processing ...")
            
        intervals = bam_chunk_interval(bam = input, nproc = nproc)
        p = Pool(nproc)
        res = p.map_async(
            functools.partial(
                bam_locate_pos_in_read,
                bam = input,
                ref_coordinate = int(locate_pos_in_read)),
                intervals.values()).get()

        res_locate = []
        for x in range(len(res)):
            res_locate += res[x]
        
        print(res_locate)
        
        if output == None:
            for x in res_locate:
                print(x)
        else:
            with open(output, "w") as f:
                for x in res_locate:
                    f.write(x + "\n")
            print("Done!")

    # locate each cigar tuple in reference coordinate for every read
    if locate_pos_in_ref:
        if output == None:
            pass
        else:
            print("Processing ...")
            
        intervals = bam_chunk_interval(bam = input, nproc = nproc)
        p = Pool(nproc)
        res = p.map_async(
            functools.partial(
                bam_locate_pos_in_ref,
                bam = input),
                intervals.values()).get()

        res_locate = []
        for x in range(len(res)):
            res_locate += res[x]
        
        if output == None:
            for x in res_locate:
                print(x)
        else:
            with open(output, "w") as f:
                for x in res_locate:
                    f.write(x + "\n")
            print("Done!")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',  '-i', type = str)
    parser.add_argument('--output', '-o', type = str, default = None)
    parser.add_argument('--locate_pos_in_read', '-lpir', default = 0)
    parser.add_argument('--num_processor', '-nproc', default = 1, type = int)

    args = parser.parse_args()
    bam(args.input, args.output, args.locate_pos_in_read, args.num_processor)

if __name__ == "__main__":
    main()
