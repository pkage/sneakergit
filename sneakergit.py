#! /usr/bin/env python
## SNEAKERGIT: an incredibly hacky "dump a repo out"
# @author Patrick Kage

import os
import shutil
import tarfile
import tempfile
import argparse
import filecmp
import re
import json

class SneakerGit:
    cfg = None
    repo = None
    target = None
    extracted = None

    patch = [];
    remove = [];

    def __init__(self, repo, target, cfg='~/.sneakergit.json'):
        self.repo = repo;
        self.target = target;
        self.cfg = json.load(open(os.path.expanduser(cfg),'r'));
        return

    def __deinit__(self):
        os.rmdir(self.extracted);

    # check if the director is excluded
    def excluded(self, fn):
        for directory in self.cfg["excluded_dirs"]:
            if re.search('(' + directory + ')(?!A-Za-z)', fn) is not None:
                return True
        return False

    def generate_diff(self):
        # declare helpers

        # traverse and create a diff
        def traverse(dcmp):
            patch = [];
            add = [];
            remove = [];

            for name in dcmp.diff_files:
                patch.append((dcmp.left, dcmp.right, name));

            for name in dcmp.left_only:
                remove.append((dcmp.left, name));

            for name in dcmp.right_only:
                add.append((dcmp.left, dcmp.right, name));

            # filter again!
            patch = [p for p in patch if not self.excluded(p[1])];
            add = [a for a in add if not self.excluded(a[1])];
            remove = [r for r in remove if not self.excluded(r[0]) and not self.excluded(r[1])];

            for sub_dcmp in dcmp.subdirs.values():
                subt = traverse(sub_dcmp)
                patch += subt[0];
                add += subt[1];
                remove += subt[2];

            return (patch, add, remove);

        # actually do the comparation
        dcmp = filecmp.dircmp(os.path.abspath(self.repo), self.extracted);
        patch, add, remove = traverse(dcmp);
        add += patch;

        self.remove = remove;
        self.add = add;

    def print_diff(self):
        # print the comparison
        for name in self.remove:
            print("remove: %s" % os.path.join(name[0], name[1]));
        for name in self.add:
            print("add: %s from %s" % (os.path.join(name[0], name[2]), os.path.join(name[1], name[2])));

    def extract_tarball(self):
        # extract a tarball
        tar = tarfile.open(self.target)
        self.extracted = os.path.join(tempfile.gettempdir(), 'sneakergit/');
        try:
            shutil.rmtree(self.extracted);
        except:
            pass;
        os.mkdir(self.extracted);
        tar.extractall(path=self.extracted);
        tar.close();

        # refer to the repo, instead of the container
        self.extracted = os.path.join(self.extracted, self.repo);
        print(self.extracted)

    def dump_tarball(self):
        # dump a tarball
        with tarfile.open(self.target, 'w:gz') as tar:
            list_dir = os.walk(self.repo);
            for root, dirs, files in list_dir:
                for filename in files:
                    toadd = os.path.join(root, filename);
                    if not self.excluded(toadd):
                        print(toadd);
                        tar.add(toadd);

    def apply_diff(self):
        # check if our user is serious
        ctd = raw_input("are you sure you want to continue (y/n)? ");
        if ctd.lower() != 'y':
            print('aborted!');
            return;
        for torem in self.remove:
            torem = os.path.join(torem[0], torem[1]);
            if os.path.isdir(torem):
                shutil.rmtree(torem);
            else:
                os.remove(torem); # weird that shutil doesn't provide this
        for tocopy in self.add:
            # [0] is the source (extracted), [1] is the destination
            tocopy = (os.path.join(tocopy[1], tocopy[2]), os.path.join(tocopy[0], tocopy[2]));
            # if we're copying over a directory, clear it out
            if os.path.isdir(tocopy[1]):
                shutil.rmtree(tocopy[1]);

            # copy!
            if os.path.isdir(tocopy[0]):
                shutil.copytree(tocopy[0], tocopy[1]);
            else:
                shutil.copy2(tocopy[0], tocopy[1]);

        print('done!')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="dump and restore a repo from a tarfile");
    parser.add_argument('operation', choices=['dump', 'diff', 'restore'], help="operation to perform");
    parser.add_argument('repo', metavar="repository", help="repository to sneak");
    parser.add_argument('target', metavar="tarfile", help="tarfile to generate/diff/restore from");
    parser.add_argument('--config', help="config file to use", required=False, default="~/.sneakergit.json")
    args = parser.parse_args();

    sg = SneakerGit(args.repo, args.target, cfg=args.config);
    if args.operation == 'diff':
        sg.extract_tarball();
        sg.generate_diff();
        sg.print_diff();
    elif args.operation == 'dump':
        sg.dump_tarball();
    elif args.operation == 'restore':
        sg.extract_tarball();
        sg.generate_diff();
        sg.print_diff();
        sg.apply_diff();
