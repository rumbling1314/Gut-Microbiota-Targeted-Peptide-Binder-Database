# Changelog

All notable changes to the **Gut Microbiota Targeted Peptide Design Database** are documented here.
This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) (`MAJOR.MINOR.PATCH`)
and the [Keep a Changelog](https://keepachangelog.com/) format.

## [Unreleased]

Rolling data additions (no version bump). The `main` branch and the online demo always
reflect the latest content.

### Added
- **Two sequence layers for every target protein.** Binder design used the mature protein after
  signal-peptide removal, so `Target_Protein` now stores both:
  `Full_Length` / `Full_Sequence` (the uncleaved original protein) and
  `AA_Length` / `Protein_Sequence` (the construct actually designed), linked by
  `Design_Region` (position of the construct in the full chain, e.g. `27-135`).
  18 of 25 targets have a construct shorter than the full protein.
- The protein-detail page now shows the design construct and, below it, the full-length
  sequence as a separate copyable card; the length line reads
  `<full> aa / Design <construct> aa (residues a-b)`.
- 6 new target proteins and 20 designed binders for previously uncovered species:
  *Christensenella minuta* (CMI), *Eubacterium ramulus* (ERA), *Mitsuokella jalaludinii* (MJA),
  *Odoribacter laneus* (OLA), *Parabacteroides distasonis* (PDI) and *Bacteroides vulgatus* (BVU).
- 160 molecular-dynamics figures (8 plots per new binder).
- Target PDB files for the 6 new species, named `<Species_ID>_target.pdb`.
- *Akkermansia muciniphila* (AMU) is now covered: target **AMU-T001** (UniProt B2UR41, the
  surface protein Amuc_1100; 317 aa design construct of a 377 aa protein) and its binder
  **AMU-T001-P001**. 25 of 32 species now carry a target and at least one binder.
- *Butyrivibrio crossotus* (BCR) now carries its real target **WP_032846860.1**
  (glycoside hydrolase family 18, BT1044-like; 323 aa mature construct of a 344 aa precursor)
  and two binders, **BCR-T001-P001** (`062_46`, dG −48.04 REU) and **BCR-T001-P002**
  (`062_86`, dG −9.34 REU).
- 16 new molecular-dynamics figures (8 per new binder, 704 in total) and the two matching
  complex PDBs.
- Localization and Pfam annotations for the six targets that had empty prediction columns
  (BVU, CMI, ERA, MJA, OLA, PDI), plus Pfam families for ten further targets.

### Changed
- **MD figures re-encoded.** Width capped at 1200 px, the fully-opaque alpha channel dropped and
  the palette reduced to 128 colours. `static/md_plots` shrank from 143.6 MB to 44.8 MB (−69%),
  so an MD page now transfers about a third of the previous bytes while the plots stay legible
  both in the page grid (380–600 px) and in the lightbox. Original files are kept in git history.
- Target PDB files are now uniformly named `<Species_ID>_target.pdb` for all species.
- Protein-detail and protein-list pages render "N/A" instead of erroring when
  localization fields are absent.
- **Localization annotation completed for all 25 targets** from the curated curation table:
  DeepLocPro location and extracellular probability 25/25, SignalP 6.0 class 25/25,
  DeepTMHMM topology 25/25; Pfam is present wherever a family hit exists (21/25, the other
  four have no Pfam hit). Signal-peptide length is recorded for the 22 targets with a signal
  peptide; the remaining three have no signal peptide at all.
- Corrected entries: BCR Outer Membrane → **Extracellular** (P = 0.9457, Sec/SPII signal
  peptide); RBR Cytoplasmic Membrane → **Extracellular** (extracellular probability
  0.0922 → 0.5016); DWE 0.9068 → 0.913 and FPR 0.4199 → 0.512 for the same quantity;
  RCA signal peptide 16 → 32 aa; signal peptide recorded for DWE (21 aa) and RIN (28 aa);
  SignalP class added for BVU/ERA (SPII) and MJA/OLA/PDI (SPI); CMI topology "No TM".
- Pfam families normalised to `PFxxxxx (name)` and updated from the curation table for
  BFR (PF20266, Mab-21_C) and CSC (PF16596, MFMR_assoc); RCA now carries
  PF22842 (Pel9A-like_beta_helix).
- The DeepTMHMM badge on the protein page shows the predicted topology directly
  (`TM` / `SP` / `beta` / `No TM`) instead of appending "no TM" to every value.

### Fixed
- `016_237` had been stored as a *B. crossotus* binder, but it is the *A. muciniphila* binder:
  the complex contains Amuc_1100 and the whole row carried that sequence together with the
  unrelated accession `D4RXI9` (a 714 aa *Butyrivibrio* penicillin-binding protein), which also
  made `Full_Length`, the Pfam family and the localization text wrong. The record is now
  **AMU-T001** / **AMU-T001-P001** with accession B2UR41, `Full_Length` 377 and Amuc_1100
  annotations.

### Fixed
- `Target_Protein.AA_Length` now records the real design-construct length for six targets where
  the value had been copied from `Full_Length`: ARE-T001 135 → 109, DWE-T001 211 → 198,
  ECL-T001 267 → 243, FPL-T001 169 → 152, RCA-T001 425 → 372, RIN-T001 332 → 323.
  `Protein_Sequence` now holds the construct that was actually designed and modelled, matching
  `static/target_pdb_files/`; `Full_Length` still records the full-length protein.
- ANB-T001 and RBR-T001 are now recorded at full length, consistent with the AF2 binder
  complexes: `AA_Length` 175 → 200 (ANB) and 106 → 130 (RBR), with the corresponding
  `Protein_Sequence`. `ANB_target.pdb` and `RBR_target.pdb` were rebuilt as full-length
  single-chain models extracted from the matching binder complex (chain B renamed to A,
  residues renumbered 1–N, provenance recorded in the header).

## [2.1.0] - 2026-10-14

Cloud deployment support.

### Added
- One-click deployment configuration for [Render](https://render.com): `Procfile`, `render.yaml`
  and `gunicorn` in `requirements.txt`.
- An online instance that lets reviewers view the database in the browser without installing Python.

### Changed
- The app now reads the `PORT` environment variable.
- Debug mode is off by default and enabled only when `FLASK_DEBUG=1`.

## [2.0.0] - 2026-10-14

Major data expansion and MD reorganization.

### Added
- 48 supplementary binders, expanding the library from 18 to **66 designed binders**
  (up to 5 binders per species where available).
- 384 additional molecular-dynamics figures (each new binder carries 8 analysis plots).
- Version management: `VERSION` file, this `CHANGELOG.md`, and a version badge on the site.
- "Binders" column on the MD list page; multi-binder grouping on the MD detail page.

### Changed
- Reorganized MD plots into `static/md_plots/<Species_ID>/<binder_design>/`
  (18 species, 66 binder designs, 528 figures).
- MD list/detail routes rewritten to support multiple binders per species, ordered P001–P005.
- Unified the GitHub repository URL across the About page, citation and footer.

### Fixed
- Corrected unit symbols to Å (RMSD) and Å² (interface buried area dSASA).
- Corrected the CSC target to **WP_252998177.1**, using the signal-peptide-cleaved mature protein.

### Removed
- Removed the mis-targeted **CEU** (*Coprococcus eutactus*) protein and binders; the species entry
  is retained and now shows no target/binder.
- Removed the unfinished **028** (*AHA*) supplementary data.

## [1.2.0] - 2026-09-29

### Added
- About page with team, affiliation, citation and contact (GitHub Issues).

## [1.1.0] - 2026-09-29

### Added
- Target protein PDB structures for the designed species.

### Fixed
- Corrected the ANB and FPR sequences.

## [1.0.0] - 2026-09-28

### Added
- Initial release of the database.
- Three-layer data model: **Species → Target_Protein → Binder**.
- 32 gut bacterial species, 18 target proteins and 18 binders.
- DeepLocPro / SignalP / DeepTMHMM / Pfam localization evidence.
- AlphaFold2 structures, Rosetta interface energies and GROMACS MD validation.
- Interactive 3D structure viewer (3Dmol.js) and PDB file download.

[2.1.0]: https://github.com/rumbling1314/Gut-Microbiota-Targeted-Peptide-Binder-Database/releases/tag/v2.1.0
[2.0.0]: https://github.com/rumbling1314/Gut-Microbiota-Targeted-Peptide-Binder-Database/releases/tag/v2.0.0
[1.2.0]: https://github.com/rumbling1314/Gut-Microbiota-Targeted-Peptide-Binder-Database/releases/tag/v1.2.0
[1.1.0]: https://github.com/rumbling1314/Gut-Microbiota-Targeted-Peptide-Binder-Database/releases/tag/v1.1.0
[1.0.0]: https://github.com/rumbling1314/Gut-Microbiota-Targeted-Peptide-Binder-Database/releases/tag/v1.0.0
