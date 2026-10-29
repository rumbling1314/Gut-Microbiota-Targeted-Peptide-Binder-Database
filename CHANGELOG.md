# Changelog

All notable changes to the **Gut Microbiota Targeted Peptide Design Database** are documented here.
This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) (`MAJOR.MINOR.PATCH`)
and the [Keep a Changelog](https://keepachangelog.com/) format.

## [Unreleased]

Rolling data additions (no version bump). The `main` branch and the online demo always
reflect the latest content.

### Added
- 7 new target proteins and 22 designed binders for previously uncovered species:
  *Christensenella minuta* (CMI), *Eubacterium ramulus* (ERA), *Mitsuokella jalaludinii* (MJA),
  *Odoribacter laneus* (OLA), *Parabacteroides distasonis* (PDI), *Bacteroides vulgatus* (BVU)
  and *Coprococcus eutactus* (CEU).
- 176 molecular-dynamics figures (8 plots per new binder).
- Target PDB files for the 7 new species, named `<Species_ID>_target.pdb`.

### Changed
- Target PDB files are now uniformly named `<Species_ID>_target.pdb` for all species.
- Protein-detail and protein-list pages render "N/A" instead of erroring when
  localization fields are absent.

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
