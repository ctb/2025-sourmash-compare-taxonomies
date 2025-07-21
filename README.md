# 2025-sourmash-compare-taxonomies

Example:
```
taxburst -F SingleM SRR11125891.profile.tsv \
    -o SRR11125891.SingleM.html \
    --save-json SRR11125891.SingleM.json

taxburst -F tax_annotate \
    SRR11125891.t0.gather.with-lineages.csv \
    -o SRR11125891.t0.taxburst.html \
    --save-json SRR11125891.sourmash.json

./compare-json-at-ranks.py \
    SRR11125891.sourmash.json \
    SRR11125891.SingleM.json \
    --remove-uncl --lowest-rank class
```
