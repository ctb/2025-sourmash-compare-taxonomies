#! /usr/bin/env python
import sys
import argparse
import json


import taxburst
from taxburst import checks


def main():
    p = argparse.ArgumentParser()
    p.add_argument('tree1_json')
    p.add_argument('tree2_json')
    args = p.parse_args()

    with open(args.tree1_json, 'rb') as fp:
        tree1 = json.load(fp)
    nodes1 = checks.collect_all_nodes(tree1)
    print(f"loaded {len(nodes1)} nodes from '{args.tree1_json}'")

    with open(args.tree2_json, 'rb') as fp:
        tree2 = json.load(fp)
    nodes2 = checks.collect_all_nodes(tree2)
    print(f"loaded {len(nodes2)} nodes from '{args.tree2_json}'")

    leaf_nodes1 = [ n for n in nodes1 if not n.get("children") ]
    leaf_nodes2 = [ n for n in nodes2 if not n.get("children") ]

    print(f"{len(leaf_nodes1)} / {len(leaf_nodes2)} leaf nodes.")

    leaf_names_1 = { n["name"] for n in leaf_nodes1 }
    leaf_names_2 = { n["name"] for n in leaf_nodes2 }
    print(f"only 1: {len(leaf_names_1 - leaf_names_2)}; only 2: {len(leaf_names_2 - leaf_names_1)}; both: {len(leaf_names_1 & leaf_names_2)}")


if __name__ == '__main__':
    sys.exit(main())
