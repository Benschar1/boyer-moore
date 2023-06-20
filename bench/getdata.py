#!/bin/python

from sys import argv, stderr
from os import path, listdir, getcwd, mkdir, remove
from shutil import rmtree
from subprocess import run
from urllib.request import urlopen
import requests
import tqdm
import tarfile

def error(msg, errcode):
    stderr.write(msg)
    exit(errcode)

def check_overwrite(file):
    if path.lexists(file):
        raise Exception(f"tried to overwrite {file}")

def datapath(*args):
    base = path.join(getcwd(), "data")
    for arg in args:
        base = path.join(base, arg)
    return base

def download(url, outfile, chunk_size=2**17):
    check_overwrite(outfile)
    print(f"downloading {outfile}")
    response = requests.get(url, stream=True)
    progress = tqdm.tqdm(
        total=int(response.headers['Content-Length']),
        unit_scale=True,
        unit_divisor=1024,
        unit=''
    )
    with open(outfile, 'wb') as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            file.write(chunk)
            progress.update(chunk_size)

def tarxf(infile, outfile):
    print(f"extracting {infile}")
    with tarfile.open(infile) as tar:
        members = tar.getmembers()
        for member in tqdm.tqdm(members, total=len(members), unit='file'):
            tar.extract(member, path=outfile)

def gunzip(infile, outfile, decompressed_size, chunk_size):
    print(f"extracting {infile}")
    check_overwrite(outfile)
    progress = tqdm.tqdm(
        total=int(decompressed_size),
        unit_scale=True,
        unit_divisor=1024,
        unit=''
    )
    txt = open(outfile, 'wb')
    with gzip.open(infile) as gz:
        while True:
            written = gz.read(chunk_size)
            l = len(written)
            if l == 0:
                break
            progress.update(l)
    txt.close()

if not path.lexists(datapath()):
    mkdir(datapath())

# recursively writes all files in a directory to an output file
# writes in alphabetical order of full filepaths
# does not follow symlinks
def catdir(infile, outfile):
    # got an UnboundLocalError without this
    # don't think 'path' is in local scope so not sure why
    from os import path
    if path.lexists(outfile):
        raise Exception(f"tried to overwrite {outfile}")

    paths = set()
    
    def rec(file):
        if path.islink(file):
            return
        file = path.realpath(file)
        if path.isfile(file):
            paths.add(file)
        elif path.isdir(file):
            for f in listdir(file):
                rec(path.join(file, f))
        else:
            # not a file, directory, or link
            return

    rec(path.realpath(infile))

    print(f"concatenating {infile} to {outfile}")
    outfile = open(outfile, "w")
    for path in tqdm.tqdm(sorted(paths), total=len(paths), unit='file'):
        f = open(path, "rb")
        outfile.write(str(f.read()))
        f.close()

    outfile.close()

if not path.lexists(datapath("king-james-bible.txt")):
    print("downloading king-james-bible.txt")
    download(
        "https://www.gutenberg.org/files/10/10-0.txt",
        datapath("king-james-bible.txt")
    )

if not path.lexists(datapath("en-subtitles.txt")):
    download(
        "https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2016/mono/en.txt.gz",
        datapath("en-subtitles.txt.gz")
    )
    gunzip(
        datapath("en-subtitles.txt.gz"),
        datapath("en-subtitles.txt"),
        decompressed_size=9968530111,
        chunk_size=2**17
    )
    remove(datapath("en-subtitles.txt.gz"))

if not path.lexists(datapath("gcc-13.1.0.txt")):
    outfile = datapath("gcc-13.1.0.tar.gz")
    download(
        "https://ftp.gnu.org/gnu/gcc/gcc-13.1.0/gcc-13.1.0.tar.gz",
        outfile
    )
    tarxf(outfile, datapath())
    remove(outfile)
    catdir(datapath("gcc-13.1.0"), datapath("gcc-13.1.0.txt"))
    rmtree(datapath("gcc-13.1.0"))

