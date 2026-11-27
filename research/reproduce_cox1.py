"""Reproducible follow-up protocol for the Ultimodel COX1 pilot."""
import argparse
import hashlib
import itertools
import json
import random
from pathlib import Path
import statistics

import Bio
from Bio import SeqIO
from Bio.Align import PairwiseAligner

SPECIES = ("human", "mouse", "arabidopsis", "yeast", "apple")
CODE = {"A": (0,0), "G": (0,1), "T": (1,0), "C": (1,1)}
DECODE = {v:k for k,v in CODE.items()}

def recover(seq):
    if set(seq) - CODE.keys():
        raise ValueError("Noncanonical DNA; preserve ambiguity separately")
    ring = [CODE[b][0] for b in seq]
    pairing = [CODE[b][1] for b in seq]
    return "".join(DECODE[p] for p in zip(ring, pairing))

def sha(b):
    return hashlib.sha256(b).hexdigest()

def read_record(path):
    rec = SeqIO.read(path, "fasta")
    seq = str(rec.seq).upper()
    if not seq:
        raise ValueError(f"Empty sequence: {path}")
    return seq, {"record_id": rec.id, "description": rec.description,
                 "file_sha256": sha(path.read_bytes()), "sequence_sha256": sha(seq.encode())}

def aligner():
    a = PairwiseAligner(mode="global")
    a.match_score = 2
    a.mismatch_score = -1
    a.open_gap_score = -5
    a.extend_gap_score = -1
    return a

def identity(a, x, y):
    # If optimal alignments tie, use Biopython's first returned alignment.
    aln = a.align(x,y)[0]
    matches = paired = 0
    for (lo,hi),(start,end) in zip(*aln.aligned):
        assert hi-lo == end-start
        paired += hi-lo
        matches += sum(p==q for p,q in zip(x[lo:hi],y[start:end]))
    return {"identity_pct": 100*matches/paired if paired else None,
            "matches": matches, "paired_positions": paired,
            "alignment_columns": aln.length, "gap_columns": aln.length-paired,
            "reference_coverage_pct": 100*paired/len(x),
            "query_coverage_pct": 100*paired/len(y), "score": aln.score}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("directory",type=Path)
    p.add_argument("--controls",type=int,default=100)
    p.add_argument("--seed",type=int,default=20261127)
    args=p.parse_args()
    if not 1 <= args.controls <= 10000:
        p.error("controls must be 1–10000")
    codons=["".join(c) for c in itertools.product(CODE,repeat=3)]
    assert all(recover(c)==c for c in codons)
    rng=random.Random(args.seed)
    a=aligner()
    out={"protocol":"explicit follow-up, not recovered original settings",
         "biopython":Bio.__version__, "seed":args.seed,"controls_per_query":args.controls,
         "alignment":{"mode":"global","match":2,"mismatch":-1,"gap_open":-5,"gap_extend":-1},
         "canonical_codons_recovered":len(codons),"species":{}}
    ref_dna=ref_protein=None
    for sp in SPECIES:
        dna, dmeta=read_record(args.directory/(sp+".fna"))
        protein, pmeta=read_record(args.directory/(sp+".faa"))
        protein=protein.removesuffix("*")
        if not protein or "*" in protein or set(protein)-set("ACDEFGHIKLMNPQRSTVWY"):
            raise ValueError(f"Noncanonical protein sequence: {sp}")
        reconstructed=recover(dna)
        assert reconstructed==dna
        if sp=="human":
            ref_dna,ref_protein=dna,protein
        result={"cds_bp":len(dna),"protein_aa":len(protein),
                "cds_source":dmeta,"protein_source":pmeta,
                "gc_pct":100*sum(b in "GC" for b in dna)/len(dna),
                "purine_pct":100*sum(b in "AG" for b in dna)/len(dna),
                "adjacent_change_pct":100*sum(x!=y for x,y in zip(dna,dna[1:]))/(len(dna)-1) if len(dna)>1 else None,
                "exact_recovery":reconstructed==dna,
                "dna_alignment":identity(a,ref_dna,dna),
                "protein_alignment":identity(a,ref_protein,protein)}
        if sp!="human":
            scores=[]
            for _ in range(args.controls):
                shuffled=list(protein)
                rng.shuffle(shuffled)
                scores.append(identity(a,ref_protein,"".join(shuffled))["identity_pct"])
            actual=result["protein_alignment"]["identity_pct"]
            result["shuffle_controls"]={"identities_pct":scores,"mean_pct":statistics.mean(scores),
                                        "max_pct":max(scores),
                                        "empirical_tail_fraction":(1+sum(s>=actual for s in scores))/(1+len(scores))}
        out["species"][sp]=result
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()
