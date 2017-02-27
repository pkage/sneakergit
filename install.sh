#! /bin/sh

# symbolic link the file
chmod +x sneakergit.py
ln -s `readlink sneakergit.py` /usr/local/bin/sneakergit

# copy the config file
cp sneakergit.json ~/.sneakergit.json
