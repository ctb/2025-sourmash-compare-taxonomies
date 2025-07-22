#! /usr/bin/env python
import sys
import argparse
import json
from collections import defaultdict

import taxburst
from taxburst import checks, taxinfo, tree_utils


def main():
    p = argparse.ArgumentParser()
    p.add_argument('treelist', nargs='+',
                   help='tree files in taxburst JSON format')
    p.add_argument('-o', '--output-json', required=True)
    
    args = p.parse_args()

    treelist = []               # may not need.
    names_to_nodes = defaultdict(list)
    total_nodes = 0

    for filename in args.treelist:
        with open(filename, 'rb') as fp:
            tree = json.load(fp)
        nodes = checks.collect_all_nodes(tree)
        print(f"loaded {len(nodes)} nodes from '{filename}'")

        for node in nodes:
            name = node["name"]
            assert name         # don't allow names to be empty
            names_to_nodes[name].append(node)

        total_nodes += len(nodes)
        treelist.append(tree)

    print(f"loaded {len(names_to_nodes)} distinct names across {total_nodes} nodes in {len(treelist)} trees.")

    # make copy of first tree...
    first_tree_copy = tree_utils.copy_tree(treelist[0])

    aug_tree = tree_utils.augment_tree(treelist[0], treelist[1:])
    aug_nodes = tree_utils.collect_all_nodes(aug_tree)

    # check that all names are in augmented tree
    found = set()
    for node in aug_nodes:
        found.add(node["name"])
    missing = set(names_to_nodes) - found
    assert not missing, len(missing)

    # check that we didn't change initial tree...
    first_tree = checks.collect_all_nodes(treelist[0])
    assert checks.trees_are_equal(first_tree, first_tree_copy)

    checks.check_structure(treelist[0])


if __name__ == '__main__':
    sys.exit(main())
