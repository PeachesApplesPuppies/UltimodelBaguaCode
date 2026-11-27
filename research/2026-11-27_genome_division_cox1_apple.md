# Ultimodel Genome Division — cross-kingdom COX1 and apple pilot
Date: 2026-11-27

## Objective
Explore information preservation across biological representations with a homologous mitochondrial gene, cytochrome c oxidase subunit I (COX1), and examine the apple as a candidate for later genome-duplication studies. These are one-gene comparisons, not whole-genome similarity estimates.

## Evidence status
The tables below transcribe the results reported in the preceding experimental conversation. The exact original FASTA files, code, alignment settings, random seeds and execution logs were not retained in the publication session, so the numerical biological results are **provisional, not independently reproduced**. The public gene identifiers have been checked against the source records; they are retrieval starting points, not hashes of the original inputs. The accompanying reproduction script specifies a new, explicit protocol; its results may differ from the earlier report. Do not treat the reported shuffled-control counts as audited significance tests.

## Complementary Lenses
Assign A=00, G=01, T=10, C=11. First bit separates purines (A,G) from pyrimidines (T,C); second separates A/T from G/C. Either bit alone has two possible bases; together they recover each base. For canonical sequences of length n, the paired streams contain 2n bits and recover the sequence exactly; this is established two-bit DNA encoding, not net compression relative to an optimal fixed-length four-symbol code. Noncanonical IUPAC symbols, gaps and other metadata require separate treatment.

The mapping is a bijection by inspection. All 64 canonical codons have unique paired representations. Exact recovery does not imply preservation of phenotype, function, epigenetic state or an entire organism.

## Previously reported COX1 comparison

| Organism | CDS bp | GC % | Purine % | Adjacent changes % | DNA identity vs human % | Protein identity vs human % |
|---|---:|---:|---:|---:|---:|---:|
| Human | 1542 | 46.24 | 43.39 | 74.63 | 100 | 100 |
| House mouse | 1545 | 39.87 | 45.63 | 73.51 | 77.78 | 90.84 |
| Arabidopsis | 1584 | 41.73 | 45.01 | 70.25 | 60.99 | 70.45 |
| Baker's yeast | 1605 | 29.91 | 45.48 | 71.45 | 59.28 | 59.41 |
| Apple | 1488 | 43.21 | 44.89 | 70.48 | 64.19 | 68.39 |

Earlier reports used aligned non-gap identity, 100% canonical DNA recovery (6,276 bases in the human/mouse/Arabidopsis/yeast comparison, 3,030 in the human/apple comparison, with human counted twice), 300 shuffled protein controls in the first comparison and 100 in the second. Apple shuffled protein mean identity was reported as 30.25%. These quantities are transcribed, not independently verified. Alignment parameters and the precise control procedure can affect identities substantially. The near-similar purine composition is a candidate observation, not an established invariant.

## Public reference identifiers
- Human: MT-CO1, NCBI Gene 4512, https://www.ncbi.nlm.nih.gov/gene/4512 ; KEGG https://www.kegg.jp/entry/hsa:4512
- Mouse: mt-Co1, NCBI Gene 17708, https://www.ncbi.nlm.nih.gov/gene/17708 ; KEGG https://www.kegg.jp/entry/mmu:17708
- Arabidopsis thaliana: ATMG01360.1, https://solgenomics.net/feature/18379157/details ; protein UniProt P60620, https://www.uniprot.org/uniprotkb/P60620/entry
- Saccharomyces cerevisiae S288C: Q0045, https://www.kegg.jp/entry/sce:Q0045 ; NCBI Gene 854598, protein NP_009305. The KEGG CDS is joined across eight exons; the entire genomic interval contains introns and is not the CDS.
- Malus domestica: cox1, NCBI Gene 13630227, protein YP_006666110, https://www.kegg.jp/entry/mdm:13630227 ; this entry explicitly lists 1,488 nt and 495 aa.

Reference protein sequences should be supplied separately from genomic CDS. Mitochondrial translation tables differ between taxa, and plant mitochondrial RNA editing can alter protein products relative to genomic DNA. Do not assume a universal standard nuclear genetic code or blindly translate plant genomic DNA.

## Apple-specific research directions
Apple's ancient whole-genome duplication, subsequent gene losses and rearrangements, hybridization and graft-based cultivar propagation offer distinct questions about persistence of information. Sexual reproduction recombines genetic information; grafting generally retains scion genotype, with possible somatic variation. The ancient nuclear duplication cannot be inferred from a single mitochondrial gene. Test it using nuclear synteny, orthogroups and duplicated gene families across Malus, Pyrus and appropriate Rosaceae outgroups; account for phylogenetic dependence, genome assembly quality, ploidy and annotation differences.

## Reproduce with a new explicit protocol
See [reproduce_cox1.py](reproduce_cox1.py). Install Biopython and provide a directory with human, mouse, arabidopsis, yeast and apple, each with a single-record .fna and .faa file named for the organism. Use annotated joined CDS and the corresponding reference protein, save original FASTA files and accession/version provenance separately. Run:

    python -m pip install biopython
    python reproduce_cox1.py /path/to/fasta --controls 100 --seed 20261127 > cox1_results.json

The script records raw-file and normalized sequence SHA-256 hashes, validates the DNA alphabet, reconstructs all canonical bases, measures composition and adjacency, uses explicit global alignment scores and seeded shuffled controls. The control identity statistic uses aligned non-gap positions with the same aligner as the observed sequence. Record gaps and alignment coverage as well. This is a fresh protocol, not a claim that the original exact settings were recovered.

## Limits
One gene, five reference taxa, no phylogenetically controlled inference, no whole-genome experiment, no evidence that genetics is a universal code of physics. The proposed conservation hypotheses require broader comparative testing. Public reference material only; no personal genome data.
