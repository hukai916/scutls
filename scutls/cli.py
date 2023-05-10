from scutls import download, fastq, barcode

# the default values are specified via the arguments.py file

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
    join   = args.join
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
    rc_barcode = args.rc_barcode,
    nproc = args.num_processor # must use full name
    )