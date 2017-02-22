#! /bin/sh

# symbolic link the file
chmod +x sneakergit.py
ln -s `realpath sneakergit.py` /usr/local/bin/sneakergit

# copy the config file
cp sneakergit.json ~/.sneakergit.json
