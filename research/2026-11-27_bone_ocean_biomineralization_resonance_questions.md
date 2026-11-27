# Bone Ocean — Resonance Division
Date: 2026-11-27
Status: research questions and proposed comparative experiments; no new sequence analyses or mechanical experiments completed.

## Central question
**How does life turn matter into an instrument?**

Can biological structures preserve comparable mechanical or sensory relationships even when the genes, materials and developmental pathways that produce them differ? This is a hypothesis about measurable relationships, not an assertion of a universal genetic code, universal frequency, or common shell-building mechanism.

## Comparative specimens
| Group | Structure to investigate | Candidate material / mechanism |
|---|---|---|
| Gastropod snails (including pond snails) | Shell growth and coiling handedness | Calcium carbonate, organic matrix |
| Scaly-foot gastropod | Shell versus dermal scales | Calcium carbonate and iron-sulfide mineralization in particular populations |
| Crabs (including blue crab) | Exoskeleton and rebuilding after molting | Chitin/protein matrix, calcium carbonate |
| Bivalves, nautiluses, barnacles | Shells or protective plates | Calcium carbonate; independently compare growth and microstructure |
| Corals and sea urchins | Mineralized skeletal elements | Calcium carbonate |
| Diatoms and glass sponges | Siliceous structures | Silica; alternative mineral chemistry controls |
| Jellyfish | Mesoglea, bell pulsation, statoliths | Hydrated organic matrix; mineralized gravity-sensing structures in relevant taxa |
| Humans and other vertebrates | Bone and inner-ear otoconia | Calcium phosphate in bone; calcium carbonate in otoconia |
| Fungi and plants (including apple) | Cell-wall scaffolds and plant mineral inclusions | Chitin-rich fungal walls; plant cellulose and, in some tissues, calcium oxalate |

The table is a specimen-selection guide, not an exhaustive taxonomic inventory. Materials vary by species, tissue, life stage and environment. Jellyfish statolith chemistry is taxon-dependent; calcium sulfate hemihydrate is a candidate in true jellyfish. Shells, exoskeletons, sensory crystals and cell walls should not be assumed homologous.

## Questions to investigate
1. Which carbonic anhydrase, chitin synthase, chitinase, tyrosinase and other mineralization-related gene families are present, expressed and functionally implicated in each tissue? Are shared genes orthologs, paralogs or independently recruited components?
2. How does the pond-snail candidate Lsdia1 connect developmental chirality to shell coiling? Can handedness, growth and material deposition be represented independently?
3. How do crabs reconstruct the geometry and mechanical properties of their exoskeleton after molting? Which variables are restored, and which change with size and developmental stage?
4. How do scaly-foot gastropods regulate mineral chemistry in shells versus scales? What is the role of local environmental chemistry?
5. How do jellyfish maintain shape and recover after deformation without a rigid shell? What contributions do collagen, fibrillin, laminin and the contractile apparatus make?
6. How do jellyfish statoliths and vertebrate otoconia convert gravity or acceleration into sensory signals? Compare mineral chemistry, crystal mass, geometry, fluid coupling, and receptor architecture without assuming shared developmental origins.
7. Which natural frequencies, damping ratios, vibration modes and transfer functions emerge from each structure? Do dimensionless mechanical relationships transfer between species after accounting for size, stiffness, density and boundary conditions?
8. Is jellyfish pulsation an internally driven rhythm, an externally entrained response, a mechanically resonant response, or a combination? Distinguish these experimentally.
9. Can incomplete structural and genetic Lenses jointly recover a measured mechanical property better than either alone? What extra information is necessary, and how much uncertainty remains?
10. Do structural relationships persist through repair, molting, growth, or evolutionary change? Which are true invariants within an explicitly defined transformation, and which are merely approximate empirical correlations?

## Proposed Ultimodel Lenses
- Magnitude: dimensions, mass, density, elastic modulus, mineral fraction and hydration.
- Polarity: chemical charge, ion gradients, material interfaces and directional response.
- Flow: rates of deposition, transport, deformation and recovery.
- Spin: chirality, orientation, rotational symmetry and mode shapes.
- Resonance: measured frequency-response functions, natural frequencies, damping, quality factor and phase.
- Recovery: changes before and after repair, molt, deformation or growth; ambiguity and supplementary information required to reconstruct a defined state.

## Proposed experiments and controls
### A. Comparative sequence analysis
Retrieve public versioned reference genomes, protein sequences, annotations and, when available, tissue-specific expression data. Start with representative gastropod, crab, jellyfish and vertebrate species. Record accessions, assembly versions, retrieval dates, hashes and license terms. Identify gene families by domain-aware homology and orthology analyses; compare gene trees with species trees. Use non-mineralizing tissues, non-shell-building relatives and shuffled-sequence controls. Presence of a gene alone does not establish its function. Candidate jellyfish sensory-development genes (including NOTUM2 and LRIG3 from the earlier literature discussion) require source and orthology verification before inclusion.

### B. Mechanical response
Use published measurements or non-invasive measurements of empty shells, shed exoskeletons and inert replicas. Record geometry, material properties, hydration, temperature, mounting, excitation and uncertainty. Start with the simple damped oscillator model m*x'' + c*x' + k*x = F(t), with undamped natural frequency f0 = sqrt(k/m)/(2*pi) where applicable. Real biological structures may require multiple modes, nonlinear models and fluid-structure coupling. Do not infer a resonant frequency from a rhythm alone; measure response to controlled frequency variation. For living jellyfish, use existing published or ethically obtained non-invasive observations, not harmful excitation.

### C. Complementary-Lens test
Define a finite state space or explicitly quantized observations, then measure the largest ambiguity fiber for each Lens and their joint observation. For a finite domain with shared ordering and deterministic observations, minimum fixed-length supplementary rank bits equal ceil(log2(maximum fiber size)). Use the existing Ouroboros engine for this discrete question. Continuous measurements require uncertainty bounds and declared resolution; prediction accuracy is not exact lossless reconstruction. Compare held-out taxa and simple physical baseline models; avoid data leakage and phylogenetic pseudoreplication.

## Falsification and interpretation
A proposed shared relationship fails if it does not predict held-out observations beyond controls, disappears after correcting for size or ancestry, or depends on arbitrary quantization. Distinguish structural similarity, homologous genes, convergent evolution, forced resonance, entrainment and self-generated rhythms. None implies the others by itself. No claim that genetics encodes the entire universe or that a universal biological resonance has been demonstrated.

## Related Ultimodel work
- [Genome Division COX1 and apple pilot](2026-11-27_genome_division_cox1_apple.md)
- [Ouroboros finite compression theorem](2026-11-27_ouroboros_compression_theorem.md)
- [Two-Eyed Ouroboros Engine](../ouroboros_engine/README.md)

**What does life preserve when it builds, moves, senses and rebuilds?**
