import urllib3
from bs4 import BeautifulSoup
import re
import importlib_resources
import json
import gzip
from mimetypes import guess_type
from functools import partial
import math
from Bio import SeqIO
from Bio.Seq import Seq
import regex

# helper function to perform sort
def num_sort(test_string):
    return list(map(int, re.findall(r'\d+', test_string)))[0]

# helper for extracting links to releases:
def get_links(url, http):
    r = http.request('GET', url)
    soup = BeautifulSoup(r.data, 'html.parser')
    a = soup.find_all('a', href = re.compile(r'^[^.]'))
    releases = [sp_h['href'].rstrip("/") for sp_h in a]
    releases = [release for release in releases if release.startswith("release-")]
    releases.sort(key=num_sort, reverse = True)
    return(releases)

# helper for extracting genome download url links:
def get_download_urls(http, ftp_site, release, genome_download_links):
    ftp_site_fasta = ftp_site + "release-" + release + "/fasta/"
    r = http.request('GET', ftp_site_fasta)
    soup = BeautifulSoup(r.data, 'html.parser')
    spcies_href = soup.find_all('a', href = re.compile(r'^[^.]'))

    species = [sp_h['href'].rstrip("/") for sp_h in spcies_href]

    for sp in species:
        genome_download_links.setdefault(sp, {})
        for k in ["gtf_md5sum", "genome_md5sum", "gtf", "genome"]:
            genome_download_links[sp].setdefault(k, None)

    species_link = [ftp_site_fasta + sp_h['href'] + "dna/" for sp_h in spcies_href]

    for i, sp_link in enumerate(species_link):
        req = http.request('GET', sp_link)
        soup = BeautifulSoup(req.data, 'html.parser')
        primary_seq_href = soup.find_all('a', href = re.compile(r'dna.primary_assembly.fa.gz'))
        toplevel_seq_href = soup.find_all('a', href = re.compile(r'dna.toplevel.fa.gz'))
        md5sum_href = soup.find_all('a', href = re.compile(r'CHECKSUMS'))

        if md5sum_href:
            genome_download_links[species[i]]["genome_md5sum"] = sp_link + md5sum_href[0]['href']
        if primary_seq_href:
            genome_download_links[species[i]]["genome"] = sp_link + primary_seq_href[0]['href']
        elif toplevel_seq_href:
            genome_download_links[species[i]]["genome"] = sp_link + toplevel_seq_href[0]['href']

    ## get gtf and gtf md5sum
    ftp_site_gtf = ftp_site + release + "/gtf/"
    r = http.request('GET', ftp_site_gtf)
    soup = BeautifulSoup(r.data, 'html.parser')
    spcies_href = soup.find_all('a', href = re.compile(r'^[^.]'))
    species_link = [ftp_site_gtf + sp_h['href']  for sp_h in spcies_href]

    species = [sp_h['href'].rstrip("/") for sp_h in spcies_href]
    for i, sp_link in enumerate(species_link):
        req = http.request('GET', sp_link)
        soup = BeautifulSoup(req.data, 'html.parser')
        gtf_href = soup.find_all('a', href = re.compile(r'\d+.gtf.gz'))
        md5sum_href = soup.find_all('a', href = re.compile(r'CHECKSUMS'))
        if md5sum_href:
            genome_download_links[species[i]]["gtf_md5sum"] = sp_link + md5sum_href[0]['href']
        if gtf_href:
            genome_download_links[species[i]]["gtf"] = sp_link + gtf_href[0]['href']
    return genome_download_links

def update_ensembl_release():
    """
    Query ENSEMBL website and update assets/genome_ensembl_release_all.txt.
    """

    http = urllib3.PoolManager()

    # get vetebrate releases: http://ftp.ensembl.org/pub/
    url = "http://ftp.ensembl.org/pub/"
    vet_releases = get_links(url, http)

    # get plant releases:
    url = "http://ftp.ensemblgenomes.org/pub/plants"
    plant_releases = get_links(url, http)

    # get fungi releases:
    url = "http://ftp.ensemblgenomes.org/pub/fungi"
    fungi_releases = get_links(url, http)

    # get metazoa releases:
    url = "http://ftp.ensemblgenomes.org/pub/metazoa"
    metazoa_releases = get_links(url, http)

    resources = importlib_resources.files("scutls")

    with open(resources / "assets" / "genome_ensembl_release_all.txt", "w") as f:
        _tem_vet = [x.split("-")[1] for x in vet_releases]
        _tem_plant = [x.split("-")[1] for x in plant_releases]
        _tem_fungi = [x.split("-")[1] for x in fungi_releases]
        _tem_metazoa = [x.split("-")[1] for x in metazoa_releases]
        f.write("vertebrates: " + ", ".join(_tem_vet) + "\n")
        f.write("plants: " + ", ".join(_tem_plant) + "\n")
        f.write("fungi: " + ", ".join(_tem_fungi) + "\n")
        f.write("metazoa: " + ", ".join(_tem_metazoa) + "\n")

def get_ensembl_url_json(vertebrates, plants, fungi, metazoa):
    """
    Extract URLs given 4 release numbers via BS.
    """
    genome_download_links = {}
    http = urllib3.PoolManager()

    ## vertebrates
    ftp_site = "http://ftp.ensembl.org/pub/"
    vertebrate_release = "release-104"
    genome_download_links = get_download_urls(http, ftp_site, vertebrates, genome_download_links)

    ## plants
    ftp_site = "http://ftp.ensemblgenomes.org/pub/plants/"
    plant_release = "release-51"
    genome_download_links = get_download_urls(http, ftp_site, plants, genome_download_links)

    ## fungi
    ftp_site = "http://ftp.ensemblgenomes.org/pub/fungi/"
    fungi_release = "release-51"
    genome_download_links = get_download_urls(http, ftp_site, fungi, genome_download_links)

    ## other metazoa
    ftp_site = "http://ftp.ensemblgenomes.org/pub/metazoa/"
    metazoa_release = "release-51"
    genome_download_links = get_download_urls(http, ftp_site, metazoa, genome_download_links)

    ## Dump the dict as json:
    resources = importlib_resources.files("scutls")
    _tem = "_".join(["genome_ensembl", vertebrates, plants, fungi, metazoa]) + ".json"
    with open(resources / "assets" / _tem , "w") as outfile:
        json.dump(genome_download_links, outfile)

# _open function that can auto handle both .gz and .fastq
def _open(filename):
    encoding = guess_type(filename)[1]  # uses file extension
    _open = partial(gzip.open, mode='rt') if encoding == 'gzip' else open
    return(_open(filename))

# find the closing number for chunking fastq file
def closest_number(n, m):
    """
    Find the closest number to n that is no less than n and also divisible by m.
    Ref: https://www.geeksforgeeks.org/find-number-closest-n-divisible-m/
    """
    q = int(n / m)
    n1 = m * q
    if((n * m) > 0) :
        n2 = (m * (q + 1))
    else :
        n2 = (m * (q - 1))

    if (abs(n - n1) < abs(n - n2)) :
        if n1 < n:
            n1 += m
        return n1
    if n2 < n:
        n2 += m
    return n2

# ensure chunk_size is a fold of 4
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# obtain the chunk intervals for given fastq and nproc
def fastq_chunk_interval(fastq, nproc = 1):
    with _open(fastq) as f:
        n1 = sum(1 for record in SeqIO.parse(f, "fastq"))
    chunk_size = math.ceil(n1 / nproc)
    chunk_size = closest_number(chunk_size, 4)
    intervals = list(chunks(range(0, n1), chunk_size))
    intervals = {i: intervals[i] for i in range(0, len(intervals))}
    return(intervals)

# obtain fastq that contains specified barcode
def fastq_contain_barcode(interval, fastq, barcode_pattern):
    fastq_hit, fastq_non_hit = [], []
    with _open(fastq) as f:
        for i, record in enumerate(SeqIO.parse(f, "fastq")):
            if i in interval:
                if regex.search(barcode_pattern, str(record.seq)):
                    fastq_hit.append(record)
                else:
                    fastq_non_hit.append(record)
    return([fastq_hit, fastq_non_hit])

# obtain search pattern given string pattern and allowed mismatches (error)
def get_search_pattern(pattern, error, rc_barcode):
    if not "," in pattern:
        if rc_barcode:
            pattern = str(Seq(pattern).reverse_complement())
        barcode_pattern = "(" + pattern + "){e<=" + str(error) + "}"
    else:
        barcode_pattern = ""
        barcodes = pattern.split(",")
        for barcode in barcodes:
            if rc_barcode:
                pattern = str(Seq(pattern).reverse_complement())
            barcode_pattern += "(" + barcode + "){e<=" + str(error) + "}(.*?)"
    return(barcode_pattern)

# obtain fastq coordinates for specified barcode
def fastq_locate_barcode(interval, fastq, barcode_pattern, pos = 0):
    """
    pos: which match to return: use 0 for the first match, use -1 for the last match.
    The return value will be: record.id match_location_0_based len(record.seq)s
    
    """
    res = []
    with _open(fastq) as f:
        for i, record in enumerate(SeqIO.parse(f, "fastq")):
            if i in interval:
                matches = regex.finditer(barcode_pattern, str(record.seq))
                # tem = [match for match in matches]
                pos_start = [match.start() for match in matches]
        
                if not len(pos_start) == 0:
                    res.append([record.id, pos_start[pos], len(record.seq)])
                else:
                    res.append([record.id, "NA", len(record.seq)])
    return(res)

if __name__ == "__main__":
    update_ensembl_release()
