import argparse
from Bio import SeqIO, bgzf
from Bio.Seq import Seq
from .util import _open, _open_out
import os

def fastq(input = None, output = None, unique = None, join = None, filter_q = None, rc = None, nproc = 1):
    """fastq subcommand
    Paramters
    ---------

    input : str
        input file name, auto detects .gz
    output : str
        output file name, auto detects .gz
    unique : str
        output unique fastq records by record ID (some bam coverted fastq may have records with duplicated IDs)
    join : str
        fastq file name to join to the input fastq, auto detects .gz
            "join" means to append each read to corresponding lines in input, not "cat"
    filter_q : int
        split reads into reads with mean_quality higher than filter_q, also output the reads failed to pass the filter into no_pass_xxx.fastq.gz.
    nproc: int
        number of parallel jobs, default to 1
        funtions that support nproc: rc

    # TODO:
    rc : str
        boolean, to reverse complement the reads, supports multi-processing

    """

    args = list(locals().keys())

    local = locals()
    if all(bool(local[key]) is not True for key in args): # use True since args can be either None or False
        print("scutls fastq: warning: use 'scutls fastq -h' for usage")

    # make fastq file unique if "-u":
    if unique:
        print("Saving to " + output + " ...")

        if not os.path.dirname(output) == "":
            os.makedirs(os.path.dirname(output), exist_ok=True)
 
        with _open(input) as f:
            unique_records = {}
            for record in SeqIO.parse(f, 'fastq'):
                if record.name not in unique_records:
                    unique_records[record.name] = record

            if output.endswith(".gz"):
                with bgzf.BgzfWriter(output, "wb") as outgz:
                    SeqIO.write(sequences = unique_records.values(), handle = outgz, format="fastq")
            else:
                SeqIO.write(unique_records.values(), output, "fastq")

        print("Done!")

    # join fastq file to input fastq if "-j":
    if join:
        print("Saving to " + output + " ...")

        if not os.path.dirname(output) == "":
            os.makedirs(os.path.dirname(output), exist_ok=True)

        f_input = _open(input)
        f_join  = _open(join)

        # sanity check: read count must match
        record_i = [record for record in SeqIO.parse(f_input, "fastq")]
        record_j = [record for record in SeqIO.parse(f_join, "fastq")]
        assert len(record_i) == len(record_j), "Number of records in --input fastq does not equal to that in --join fastq!"

        if output.endswith(".gz"):
            f_out = bgzf.BgzfWriter(output, "wb")
        else:
            f_out = open(output, "w")

        for i in range(len(record_i)):
            _record = record_i[i]
            _record_j = record_j[i]

            # sanity check: read description must match
            assert _record.description == _record_j.description, "Read description in --input fastq does not match with --join fastq!"
            record_quality = ''.join(map(lambda x: chr(x + 33), _record.letter_annotations["phred_quality"]))
            record_j_quality = ''.join(map(lambda x: chr(x + 33), _record_j.letter_annotations["phred_quality"]))

            f_out.write("@" + _record.description + "\n")
            f_out.write(str(_record.seq) + str(_record_j.seq) + "\n")
            f_out.write("+\n")
            f_out.write(record_quality + record_j_quality + "\n")

        f_input.close()
        f_join.close()
        f_out.close()
        print("Done!")

    # filter reads based on mean quality cutoff if "-fq":
    if filter_q:
        filter_q = int(filter_q)
        if not os.path.dirname(output) == "":
            os.makedirs(os.path.dirname(output), exist_ok=True)
        
        output2 = os.path.join(os.path.dirname(output), "not_pass_" + os.path.basename(output))
        print("Saving to " + output + " ...")
        print("Saving to " + output2 + " ...")

        with _open(input) as f, _open_out(output) as f_out, _open_out(output2) as f_out2:
            for record in SeqIO.parse(f, "fastq"):
                mean_quality = sum(record.letter_annotations["phred_quality"]) / len(record)
                if mean_quality >= filter_q:
                    SeqIO.write(record, f_out, "fastq")
                else:
                    SeqIO.write(record, f_out2, "fastq")
                    
        print("Done!")

    
    # reverse complement fastq if "-rc":
    # todo

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',  '-i', type   = str)
    parser.add_argument('--output', '-o', type   = str)
    parser.add_argument('--unique', '-u', action = 'store_true')
    parser.add_argument('--join',   '-j', type   = str)

    args = parser.parse_args()
    fastq(args.input, args.output, args.unique, args.join)

if __name__ == "__main__":
    main()
