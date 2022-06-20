from scutls import download

def run_download(options):
    download.download(
    list_genome_ucsc = options.list_genome_ucsc,
    genome_ucsc = options.genome_ucsc,
    outdir = options.outdir
    )
