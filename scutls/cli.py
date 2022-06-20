from scutls import download

def run_download(args):
    download.download(
    list_genome_ucsc = args.list_genome_ucsc,
    genome_ucsc = args.genome_ucsc,
    list_genome_ensembl = args.list_genome_ensembl,
    genome_ensembl = args.genome_ensembl,
    outdir = args.outdir
    )
