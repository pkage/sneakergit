# __sneakergit__ - because sometimes you need to work outside of git
---

## dependencies

100% pure python

## install

```bash
$ ./install.sh
```
_if `/usr/local/bin/` is not writeable, you may need sudo_

## usage

```
usage: sneakergit [-h] [--config CONFIG]
                  {dump,diff,restore} repository tarfile

dump and restore a repo from a tarfile

positional arguments:
  {dump,diff,restore}  operation to perform
  repository           repository to sneak
  tarfile              tarfile to generate/diff/restore from

optional arguments:
  -h, --help           show a help message and exit
  --config CONFIG      config file to use

```

