# Duplicate file checker
```
usage: hashdup.py [-h] [-r] [-i] [-a algorithm] [-q] [--ad number] path

duplicate file checker - by /robex/

positional arguments:
  path                  path to check

options:
  -h, --help            show this help message and exit
  -r, --recurse         recursive, check files from all subdirectories
  -i, --interactive     prompt for deletion of duplicate files
  -a algorithm          hashing algorithm to use (xxhash, sha1, sha256), default sha1
  -q, --quick-hash      hash only a small percentage of the file. WARNING: doesn't guarantee the files are exactly
                        equal!
  --ad, --auto-delete number
                        WARNING! automatically delete specified duplicate files ('number' is what you would type
                        manually with -i)
```
