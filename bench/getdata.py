#!/bin/python

from yaml import load_all, dump_all, Loader, Dumper, YAMLError
from pprint import pprint
from sys import argv, stderr
from os import path, listdir, getcwd, mkdir, remove
from shutil import rmtree
from subprocess import run
from urllib.request import urlopen
import requests
import tqdm
import tarfile
import tempfile

def error(msg, errcode):
    stderr.write(msg)
    exit(errcode)

def check_overwrite(file):
    if path.lexists(file):
        raise Exception(f"tried to overwrite {file}")

def datapath(*args):
    base = path.join(getcwd(), "bench", "data")
    for arg in args:
        base = path.join(base, arg)
    return base

def download(url, outfile, chunk_size=2**17):
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

cases_file = open(path.join(getcwd(), "bench", "fixed-substring.yaml"), "r")
cases_obj = load_all(cases_file, Loader=Loader)

for obj in cases_obj:
    filepath = datapath(obj['file'])
    if path.lexists(filepath):
        print(f"{filepath} exists, delete and rerun to redownload")
    url = obj['source']['url']
    match obj['source']['format']:
        case 'text':
            download(url, filepath)
        case 'targz':
            (_, temp_path) = tempfile.mkstemp(suffix='.tar.gz')
            download(url, temp_path)
            tarxf(temp_path, filepath)
            remove(temp_path)
        case _:
            print(f"failed getting {obj['file']}, format not implemented")

'''
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
'''

