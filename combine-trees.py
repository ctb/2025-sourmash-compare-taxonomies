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

    # build an augmented tree that contains all the nodes
    aug_tree = tree_utils.augment_tree(treelist[0], treelist[1:])
    aug_nodes = tree_utils.collect_all_nodes(aug_tree)

    # we can now adjust the nodes in the aug_tree however we want:
    for adj_node in aug_nodes:
        name = adj_node["name"]
        orig_nodes = names_to_nodes[name]
        mean_count = sum([ n["count"] for n in orig_nodes ]) / len(orig_nodes)
        adj_node["count"] = mean_count

    with open(args.output_json, "w") as fp:
        json.dump(aug_tree, fp)
    print(f"saved {len(aug_nodes)} nodes to '{args.output_json}'")


if __name__ == '__main__':
    sys.exit(main())
