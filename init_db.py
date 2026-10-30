"""
初始化数据库 - 严格按Excel参考表结构
3张表: Species / Target_Protein / Binder
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "binder_db.db")

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"已删除旧数据库: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Species 菌种表（表头完全按Excel）
    c.execute("""
    CREATE TABLE Species (
        Species_ID      TEXT PRIMARY KEY,
        Scientific_Name TEXT NOT NULL,
        Chinese_Name    TEXT,
        Taxonomy_ID     INTEGER,
        Genome_Accession TEXT,
        Proteome_Source TEXT,
        Notes           TEXT
    )
    """)

    # 2. Target_Protein 靶蛋白表（含定位预测：DeepLocPro/SignalP/DeepTMHMM/Pfam）
    #    Two sequence layers: Full_Sequence/Full_Length = the uncleaved original protein,
    #    AA_Length/Protein_Sequence = the construct actually used for design, with
    #    Design_Region recording where that construct sits in the full chain (e.g. 27-135).
    c.execute("""
    CREATE TABLE Target_Protein (
        Species_ID            TEXT NOT NULL,
        Protein_ID            TEXT PRIMARY KEY,
        ID_Accession          TEXT,
        Full_Length           INTEGER,
        AA_Length             INTEGER,
        Protein_Sequence      TEXT,
        Localization_Evidence TEXT,
        DeepLocPro_Location   TEXT,
        DeepLocPro_ExtProb    REAL,
        SignalP_Category      TEXT,
        SignalP_SPLen         INTEGER,
        DeepTMHMM_Type        TEXT,
        Pfam_Family           TEXT,
        Notes                 TEXT,
        Full_Sequence         TEXT,
        Design_Region         TEXT,
        FOREIGN KEY (Species_ID) REFERENCES Species(Species_ID)
    )
    """)

    # 3. Binder 多肽表（含 Rosetta 界面能量 + AF2 质量指标）
    c.execute("""
    CREATE TABLE Binder (
        Binder_ID       TEXT PRIMARY KEY,
        Species_ID      TEXT NOT NULL,
        Binder_Sequence TEXT,
        Length          INTEGER,
        Raw_Score       REAL,
        dG_sep_norm     REAL,
        dSASA_int       REAL,
        complex_norm    REAL,
        total_score     REAL,
        packstat        REAL,
        hbonds_int      INTEGER,
        pLDDT_total     REAL,
        pLDDT_binder    REAL,
        PAE_interaction REAL,
        binder_RMSD     REAL,
        target_RMSD     REAL,
        Sequence_File   TEXT,
        Structure_File  TEXT,
        Notes           TEXT,
        FOREIGN KEY (Species_ID) REFERENCES Species(Species_ID)
    )
    """)

    c.execute("CREATE INDEX idx_protein_species ON Target_Protein(Species_ID)")
    c.execute("CREATE INDEX idx_binder_species ON Binder(Species_ID)")

    conn.commit()
    conn.close()
    print(f"数据库已创建: {DB_PATH}")
    print("3张表: Species, Target_Protein, Binder")

if __name__ == "__main__":
    init_db()
