# Gut Microbiota Targeted Peptide Design Database

![Release](https://img.shields.io/badge/release-v2.1.0-27ae60)
![Species](https://img.shields.io/badge/species-32-2980b9)
![Targets](https://img.shields.io/badge/target_proteins-18-2980b9)
![Binders](https://img.shields.io/badge/binders-66-27ae60)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

### A Bioinformatics Resource for Identifying Functional Bacteria in the Complex Gut Microbiota

> **Live online demo:** <https://gut-peptide-design-db.onrender.com>
> Browse the full database in your browser without installation (the free instance sleeps when idle;
> the first request may take about 50 seconds to wake up).

> **Current release: v2.1.0** (2026-10-14). For the full version history see
> [CHANGELOG.md](CHANGELOG.md) and the [GitHub Releases](https://github.com/rumbling1314/Gut-Microbiota-Targeted-Peptide-Binder-Database/releases).

A Python Flask + SQLite web resource for the design of targeting peptides (binders) against
surface proteins of gut bacteria. The data model is organized in three layers:

**Species → Target_Protein → Binder**

- **Species** — 32 gut bacterial strains
- **Target_Protein** — selected surface target proteins (one per strain), with localization
  predictions from DeepLocPro, SignalP, DeepTMHMM and Pfam
- **Binder** — targeting peptides designed with RFdiffusion + ProteinMPNN, with AlphaFold2
  predicted structures, Rosetta interface energies and molecular-dynamics (GROMACS) validation

## Quick Start

The database file `binder_db.db` is shipped with the project and already contains all data.
The easiest way to browse it:

```bash
pip install -r requirements.txt   # install dependencies (once)
python app.py                     # start the web server
# open http://127.0.0.1:5000 in your browser
```

To rebuild the database from the CSV files (note: `init_db.py` drops and recreates an empty
database, so existing data will be cleared):

```bash
python init_db.py        # 1. create the three tables (clears the old database)
python batch_import.py   # 2. import the 32 species and the CSVs under data/
python app.py            # 3. start the web server
```

## Project Structure

```
.
├── app.py              # Flask web application
├── init_db.py          # database schema creation (three tables)
├── batch_import.py     # import script (32 species built-in; also imports data/ CSVs)
├── binder_db.db        # SQLite database (already populated)
├── requirements.txt
├── README.md
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html          # home (overview statistics)
│   ├── species.html        # species list
│   ├── species_detail.html # species detail
│   ├── proteins.html       # target protein list
│   ├── protein_detail.html # target protein detail
│   ├── binders.html        # binder list
│   ├── binder_detail.html  # binder detail (3D structure + download)
│   ├── md.html             # molecular-dynamics analysis list
│   └── md_detail.html      # molecular-dynamics plots for one species
├── static/
│   ├── pdb_files/          # AlphaFold2 predicted binder complex structures (.pdb, chain A=binder, B=target)
│   ├── target_pdb_files/   # target protein structures used for binder design (.pdb)
│   ├── md_plots/           # GROMACS analysis plots, <Species_ID>/<binder_design>/ (8 plots per binder)
│   └── VERSION             # current semantic version
└── data/                   # import data
    ├── proteins.csv        # target proteins (24 rows)
    ├── proteins.xlsx       # target proteins (formatted spreadsheet)
    └── binders.csv         # binders (86 rows, 19 columns)
```

## Routes

| Route | Page | Description |
|---|---|---|
| `/` | Home | counts of species / proteins / binders and top binders |
| `/species` | Species list | all 32 species, keyword search via `?q=` |
| `/species/<Species_ID>` | Species detail | target proteins and binders of one species |
| `/proteins` | Target protein list | searchable |
| `/proteins/<Protein_ID>` | Target protein detail | protein sequence, target 3D structure (PDB download) and related binders |
| `/binders` | Binder list | sorted by Raw_Score, searchable |
| `/binders/<Binder_ID>` | Binder detail | sequence, scores, interactive 3D structure, PDB download |
| `/md` | MD analysis list | species with molecular-dynamics plots |
| `/md/<Species_ID>` | MD analysis detail | 8 GROMACS plots (RMSD, RMSF, Rg, H-bonds, min distance, temperature, pressure, potential) |

## Database Schema

| Table | Purpose | Key fields |
|---|---|---|
| Species | 32 strains | Species_ID (PK), Scientific_Name, Chinese_Name, Taxonomy_ID, Genome_Accession, Proteome_Source, Notes |
| Target_Protein | surface target proteins | Protein_ID (PK), Species_ID (FK), ID_Accession, Full_Length, Full_Sequence, AA_Length, Design_Region, Protein_Sequence, Localization_Evidence, DeepLocPro_Location, DeepLocPro_ExtProb, SignalP_Category, SignalP_SPLen, DeepTMHMM_Type, Pfam_Family, Notes |
| Binder | designed targeting peptides | Binder_ID (PK), Species_ID (FK), Binder_Sequence, Length, Raw_Score, dG_sep_norm, dSASA_int, complex_norm, total_score, packstat, hbonds_int, pLDDT_total, pLDDT_binder, PAE_interaction, binder_RMSD, target_RMSD, Sequence_File, Structure_File, Notes |

- `Target_Protein.Species_ID` and `Binder.Species_ID` both reference `Species.Species_ID`.
- **Localization fields (target proteins):**
  - `ID_Accession` — protein accession (upper case).
  - **Two sequence layers per target.** Binder design was run on the mature protein after
    signal-peptide removal, so both layers are stored:
    - `Full_Length` / `Full_Sequence` — the uncleaved original protein (as annotated at the
      accession) and its complete sequence;
    - `AA_Length` / `Protein_Sequence` — the construct actually used for design, and
      `Design_Region` — where that construct sits in the full chain (1-based, e.g. `27-135`).
    When no cleavage was applied `Design_Region` is `1-<Full_Length>` and both sequences are
    identical. The target structures under `static/target_pdb_files/` follow the same split:
    the ATOM records are the design construct, the SEQRES header the full-length chain.
  - `DeepLocPro_Location` / `DeepLocPro_ExtProb` — DeepLocPro 2 localization and extracellular probability.
  - `SignalP_Category` / `SignalP_SPLen` — SignalP 6.0 signal-peptide class (SPI / SPII lipoprotein / OTHER) and length.
  - `DeepTMHMM_Type` — DeepTMHMM topology (SP no TM / TM / SP+TM).
  - `Pfam_Family` — Pfam protein families / domains.
  - `Localization_Evidence` — detailed localization conclusion integrating the four tools,
    including the extracellular accessible region.
- **Binder energy and quality fields** (Rosetta from the pack-input score summary, AF2 from the output summary):
  - Rosetta interface energy: `Raw_Score` (= dG_separated interface binding free energy, REU, primary metric),
    `dG_sep_norm` (dG/dSASA×100 normalized), `dSASA_int` (interface buried area),
    `complex_norm`, `total_score`, `packstat`, `hbonds_int` (interface hydrogen bonds).
  - AlphaFold2 quality: `pLDDT_total`, `pLDDT_binder`, `PAE_interaction`, `binder_RMSD`, `target_RMSD`.
  - A more negative Raw_Score means more favorable binding. `Binder.Structure_File` points to a
    PDB under `static/pdb_files/` (chain A = binder, chain B = target).

## Import Your Own Data

Organize your results into CSVs in the `data/` directory (column names matching the existing
headers), then run `python batch_import.py`. It uses `INSERT OR REPLACE`, updating by primary key
without clearing other data.

CSVs should be UTF-8 encoded (BOM allowed). The import script casts length/count columns to
integers and score/probability columns to floats automatically.

## Current Status

- Species: all 32 imported
- Target proteins + binders: completed for **24 species**, with **86 binders** in total
  (up to 5 binders per species)
- Pending: 8 species have no target protein or binder yet

## Toolchain

- RFdiffusion v1.1.0 — backbone generation
- dl_binder_design (cafa3853) — binder design pipeline
- ProteinMPNN (8907e66) — sequence design
- silent_tools 1.0.0 — silent-file processing
- Rosetta 2024.09 (release-371) — energy scoring and interface analysis
- AlphaFold2 (params 2022-12-06) — structure prediction
- GROMACS 2025.0 — molecular-dynamics validation

## License

Released under the MIT License. See [LICENSE](LICENSE).
