from scutls import download, fastq, barcode, bam

# the default values are specified via the arguments.py file
# should use full argument name for both left and right side

def run_download(args):
    download.download(
    list_genome_ucsc = args.list_genome_ucsc,
    genome_ucsc = args.genome_ucsc,
    list_genome_ensembl = args.list_genome_ensembl,
    genome_ensembl = args.genome_ensembl,
    annotation_ucsc = args.annotation_ucsc,
    annotation_ensembl = args.annotation_ensembl,
    ensembl_release = args.ensembl_release,
    ensembl_release_use = args.ensembl_release_use,
    ensembl_release_update = args.ensembl_release_update,
    outdir = args.outdir
    )

def run_fastq(args):
    fastq.fastq(
    input  = args.input,
    output = args.output,
    unique = args.unique,
    join   = args.join,
    filter_q = args.filter_q
    )

def run_bam(args):
    bam.bam(
    input  = args.input,
    output = args.output,
    locate_pos_in_read = args.locate_pos_in_read,
    locate_pos_in_ref = args.locate_pos_in_ref,
    nproc = args.num_processor
    )

def run_barcode(args):
    barcode.barcode(
    input  = args.input,
    output = args.output,
    output2 = args.output2,
    contain = args.contain,
    locate = args.locate,
    pos = args.position,
    error   = args.error,
    mismatch_only = args.mismatch_only,
    rc_barcode = args.rc_barcode,
    nproc = args.num_processor # must use full name
    )