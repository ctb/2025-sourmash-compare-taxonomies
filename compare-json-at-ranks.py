#! /usr/bin/env python
import sys
import argparse
import json
from collections import defaultdict
import pandas as pd
import taxburst
from taxburst import checks


taxinfo_ranks = [
    "superkingdom",
    "phylum",
    "class",
    "order",
    "family",
    "genus",
    "species",
    "strain",
    "genome",
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('tree1_json')
    p.add_argument('tree2_json')
    p.add_argument("--output", help="Path to output CSV file")
    p.add_argument('--diff-fraction-tolerance', type=float, default=.01)
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
        found_unclassified = False
        tree1_filt = []
        for n in tree1:
            if n["name"] == 'unclassified':
                print(f"removing 'unclassified' from first")
                found_unclassified = True
            else:
                tree1_filt.append(n)

        tree2_filt = []
        for n in tree2:
            if n["name"] == 'unclassified':
                print(f"removing 'unclassified' from second")
                found_unclassified = True
            else:
                tree2_filt.append(n)

        tree1 = tree1_filt
        tree2 = tree2_filt

        nodes1 = checks.collect_all_nodes(tree1)
        nodes2 = checks.collect_all_nodes(tree2)
        
        if not found_unclassified:
            print("ERROR: --remove-unclassified was specified, but no unclassified was found. Adjust your expectations, please.")
            assert 0, "you were wrong, dude"

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

    print(f"{'rank':<15} {'name':<30}  {'diff':>4}")
    print(f"------------    ------------                    ----")

    ranks = list(taxinfo_ranks)
    ranks.reverse()
    if args.lowest_rank:
        idx = ranks.index(args.lowest_rank)
        ranks = ranks[idx:]
    rows = []
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
                f2 = node2["count"] / total_count_2

            f1 = node1["count"] / total_count_1
            diffs.append((rank, name, f1, f2, abs(f1 - f2)))


        for node2 in nodes_by_rank_2[rank]:
            name = node2["name"]
            if name in seen:
                continue
            seen.add(name)
            node1 = nodes_by_name_1.get(name)

            f1 = 0
            if node1 is not None:
                f1 = node1["count"] / total_count_1

            f2 = node2["count"] / total_count_2
            diffs.append((rank, name, f1, f2, abs(f1-f2)))

        
        diffs.sort(key=lambda x: -x[4])
        for (rank, name, f1, f2, diff) in diffs:
            rows.append({
                "rank": rank,
                "name": name,
                "diff": (f1 - f2) * 100,
                "first_tax": f1 * 100,
                "second_tax": f2 * 100
            })
            if diff > args.diff_fraction_tolerance:
                print(f"{rank:<15} {name:<30} {(f1 - f2)*100:>4.1f}%    {f1*100:>4.1f}% / {f2*100:>4.1f}%")

        if args.output:
            df_out = pd.DataFrame(rows, columns=["rank", "name", "diff", "first_tax", "second_tax"])
            df_out.to_csv(args.output, index=False)

if __name__ == '__main__':
    sys.exit(main())
