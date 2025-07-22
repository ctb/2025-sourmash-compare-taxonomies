#! /usr/bin/env python
import sys
import argparse
import json
from collections import defaultdict

import taxburst
from taxburst import checks, taxinfo


def main():
    p = argparse.ArgumentParser()
    p.add_argument('tree1_json')
    p.add_argument('tree2_json')
    p.add_argument('--diff-tolerance', type=float, default=0)
    p.add_argument('--remove-unclassified', action='store_true',
                   help="remove top-level unclassified before calculating fractions of total")
    p.add_argument('--lowest-rank', default="genome",
                   help="lowest rank for which to report results")
    p.add_argument('--rank', default=None,
                   help="report only for this rank")
    
    args = p.parse_args()

    with open(args.tree1_json, 'rb') as fp:
        tree1 = json.load(fp)
    nodes1 = checks.collect_all_nodes(tree1)
    print(f"loaded {len(nodes1)} nodes from '{args.tree1_json}'")

    with open(args.tree2_json, 'rb') as fp:
        tree2 = json.load(fp)
    nodes2 = checks.collect_all_nodes(tree2)
    print(f"loaded {len(nodes2)} nodes from '{args.tree2_json}'")

    if args.remove_unclassified:
        nodes1_filt = []
        for n in nodes1:
            if n["name"] == 'unclassified':
                print(f"removing 'unclassified' from first")
            else:
                nodes1_filt.append(n)
        nodes1 = nodes1_filt

        nodes2_filt = []
        for n in nodes2:
            if n["name"] == 'unclassified':
                print(f"removing 'unclassified' from second")
            else:
                nodes2_filt.append(n)
        nodes2 = nodes2_filt

    total_count_1 = sum([float(n["count"]) for n in tree1])
    total_count_2 = sum([float(n["count"]) for n in tree2])

    nodes_by_rank_1 = defaultdict(list)
    nodes_by_name_1 = {}
    for node in nodes1:
        rank = node["rank"]
        nodes_by_rank_1[rank].append(node)
        name = node["name"]
        assert name not in nodes_by_name_1
        nodes_by_name_1[name] = node
        
    nodes_by_rank_2 = defaultdict(list)
    nodes_by_name_2 = {}
    for node in nodes2:
        rank = node["rank"]
        nodes_by_rank_2[rank].append(node)
        name = node["name"]
        assert name not in nodes_by_name_2
        nodes_by_name_2[name] = node

    print(f"{'rank':<15} {'name':<30}  {'loss':>5}")
    print(f"------------    ------------                   ------")

    ranks = taxinfo.ranks
    ranks.reverse()
    if args.lowest_rank:
        idx = ranks.index(args.lowest_rank)
        ranks = ranks[idx:]

    for rank in ranks:
        if args.rank and args.rank != rank:
            continue

        diffs = []
        seen = set()
        for node1 in nodes_by_rank_1[rank]:
            name = node1["name"]
            seen.add(name)
            node2 = nodes_by_name_2.get(name)

            f2 = 0
            if node2 is not None:
                f2 = int(node2["count"])

            f1 = int(node1["count"])
            diffs.append((rank, name, f1, f2, (f1 - f2) / f1))


        for node2 in nodes_by_rank_2[rank]:
            name = node2["name"]
            if name in seen:
                continue
            seen.add(name)
            node1 = nodes_by_name_1.get(name)

            f1 = 0
            if node1 is not None:
                f1 = int(node1["count"])

            f2 = int(node2["count"])
            diffs.append((rank, name, f1, f2, (f1 - f2)/f1))

        diffs.sort(key=lambda x: -x[4])
        for (rank, name, f1, f2, diff) in diffs:
            if diff > args.diff_tolerance:
                print(f"{rank:<15} {name:<30} {diff*100:>-5.1f}%    {f1:>8d} / {f2:>8d}")


if __name__ == '__main__':
    sys.exit(main())
