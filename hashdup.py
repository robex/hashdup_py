#!/usr/bin/python3

import os
import argparse
import operator
import itertools
import hashlib
import xxhash

CHUNKSZ = 2**20
g_args = None

class HFile:
    def __init__(self, fname):
        self.fname = fname
        self.size = 0
        self.hash = 0
        self.deleted = False

def parse_args():
    parser = argparse.ArgumentParser(description = "duplicate file checker - by /robex/")
    parser.add_argument("-r", "--recurse", help = "recursive, check files from all subdirectories", action = "store_true")
    parser.add_argument("-i", "--interactive", help = "prompt for deletion of duplicate files", action = "store_true")
    parser.add_argument("-a", metavar = "algorithm", type = str, help = "hashing algorithm to use (xxhash, sha1, sha256), default sha1")
    parser.add_argument("-q", "--quick-hash", help = "hash only a small percentage of the file. WARNING: doesn't guarantee the files are exactly equal!", action = "store_true")
    parser.add_argument("--ad", "--auto-delete", metavar = "number", type = str, help = "WARNING: automatically delete specified duplicate files ('number' is what you would type manually with -i) ")
    parser.add_argument("path", help = "path to check")

    args = parser.parse_args()
    return args

def sort_file_list(files):
    keyfun = operator.attrgetter("size")
    files.sort(key = keyfun, reverse=True)

def print_file_list(files):
    for file in files:
        print(file.fname)
        print(file.size)
        print(file.hash)
        print(file.deleted)

def get_file_list():
    hfiles = []

    for root, dirs, files in os.walk(g_args.path):
        for fname in files:
            p = os.path.join(root, fname)
            f = HFile(p)
            f.size = os.path.getsize(p)
            hfiles.append(f)
        if not g_args.recurse:
            break
            
    sort_file_list(hfiles)
    # print_file_list(hfiles)

    return hfiles

def calc_hash(fobj):
    hash_obj = hashlib.sha1() 

    if g_args.a == "sha1":
        hash_obj = hashlib.sha1() 
    elif g_args.a == "sha256":
        hash_obj = hashlib.sha256() 
    elif g_args.a == "xxhash":
        hash_obj = xxhash.xxh3_64()

    with open(fobj.fname, "rb") as f:
        if g_args.quick_hash and fobj.size > CHUNKSZ * 3:
            # beginning of file
            chunk = f.read(CHUNKSZ)
            hash_obj.update(chunk)

            # middle of file
            f.seek(fobj.size // 2 - CHUNKSZ // 2)
            chunk = f.read(CHUNKSZ)
            hash_obj.update(chunk)

            # end of file
            f.seek(fobj.size - CHUNKSZ)
            chunk = f.read(CHUNKSZ)
            hash_obj.update(chunk)
        else:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_obj.update(chunk)

    return hash_obj.hexdigest().lower()

def handle_duplicates(dupl):
    ndup = len(dupl)
    for i, f in enumerate(dupl):
        print("(" + str(i) + ") [" + f.hash[0:8] + "] " + "size: " + str(f.size) + " B, '" + f.fname + "'")

    if not g_args.interactive and not g_args.ad:
        print()
    else:
        fdel = ""
        if g_args.ad:
            fdel = g_args.ad
        else:
            fdel = input("select files to delete (0-" + str(ndup - 1) + "/q), default q: ")

        if fdel == "q" or fdel == "":
            print()
            return
        try:
            fdels = fdel.split(",")
            if len(fdels) < ndup:
                for i in fdels:
                    i = int(i)
                    if i >= 0 and i < ndup: 
                        if os.path.isfile(dupl[i].fname):
                            os.remove(dupl[i].fname)
                            dupl[i].deleted = True
                            print("deleted " + dupl[i].fname + "\n")
                    else:
                        print("error: number outside of valid range")
        except ValueError:
            print("invalid/not a number")

def find_duplicates(files):
    kf1 = operator.attrgetter("size")
    kf2 = operator.attrgetter("hash")

    for k1, g1 in itertools.groupby(files, kf1):
        g1 = list(g1)
        # different files with same size
        if len(g1) == 1:
            continue

        for f in g1:
            f.hash = calc_hash(f)

        # different files with the same hash
        for k2, g2 in itertools.groupby(g1, kf2):
            g2 = list(g2)
            if len(g2) == 1:
                continue

            handle_duplicates(g2)

def __main__():
    global g_args
    g_args = parse_args()
    files = get_file_list()
    find_duplicates(files)

__main__()
