"""
批量导入脚本
用法:
  1. python init_db.py （第一次建库）
  2. python batch_import.py （导入32菌种 + data/下的csv）
"""
import sqlite3
import os
import csv

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "binder_db.db")
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# 32个菌种数据（从Excel提取）
SPECIES_DATA = [
    ("FPR", "Faecalibacterium prausnitzii", "普氏栖粪杆菌", 853, "GCF_000154385.1", "NCBI RefSeq (GCF),Uniprot", "装配对应菌株 M21/2；Research focus: anti-inflammatory, CKD, atherosclerosis, IBD"),
    ("BVU", "Bacteroides vulgatus", "普通拟杆菌", 821, "GCF_000012825.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: metabolic syndrome; insulin resistance and ovarian dysfunction"),
    ("ARE", "Agathobacter rectalis", "直肠真杆菌", 39491, "GCF_022453685.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: intestinal immune homeostasis, inflammation suppression, gut-brain axis"),
    ("RBR", "Ruminococcus bromii", "酒神瘤胃球菌", 40518, "GCF_928721825.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: SCFA enhancement, metabolic health"),
    ("BWE", "Blautia wexlerae", "韦氏布劳特氏菌", 418240, "GCF_025148125.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: obesity, T2DM"),
    ("FSA", "Fusicatenibacter saccharivorans", "食蔗糖纺锤状链杆菌", 1150298, "GCF_027667425.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: metabolic-associated fatty liver disease, long COVID biomarker"),
    ("AHA", "Anaerostipes hadrus", "宠大厌氧棒状菌", 649756, "GCF_030864025.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: primary Sjögren's syndrome, glucose metabolism"),
    ("PFA", "Phascolarctobacterium faecium", "粪考拉杆菌", 33025, "GCF_003945365.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: obesity control (PYY signaling)"),
    ("RFA", "Roseburia faecis", "粪便罗斯拜瑞氏菌", 301302, "GCF_045061065.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: metabolic syndrome, IBD, diabetes"),
    ("CEU", "Coprococcus eutactus", "伴生粪球菌", 33043, "GCF_025149915.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: autism-related"),
    ("BCR", "Butyrivibrio crossotus", "穗状丁酸弧菌", 45851, "GCF_025148445.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: positively associated with fiber intake, negatively associated with T2DM"),
    ("AMU", "Akkermansia muciniphila", "嗜黏蛋白阿克曼氏菌", 239935, "GCF_009731575.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: obesity, diabetes, metabolic syndrome"),
    ("ASH", "Alistipes shahii", "沙氏别样杆菌", 328814, "GCF_025145845.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: IBS comorbid with affective disorders"),
    ("PDI", "Parabacteroides distasonis", "狄氏副拟杆菌", 823, "GCF_018279895.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: obesity/metabolism, bladder cancer, NASH"),
    ("BOV", "Bacteroides ovatus", "卵形拟杆菌", 28116, "GCF_001314995.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: atherosclerosis"),
    ("ANB", "Anaerobutyricum hallii", "霍氏厌氧丁酸菌", 39488, "GCF_018140635.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: anti-inflammatory, intestinal barrier repair"),
    ("BFR", "Bacteroides fragilis", "脆弱拟杆菌（NTBF）", 817, "GCF_000025985.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: non-toxigenic strain; alleviates depression, ASD"),
    ("MJA", "Mitsuokella jalaludinii", "贾氏光冈菌", 187979, "GCF_928722185.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: phytic acid-driven health benefits"),
    ("BTH", "Bacteroides thetaiotaomicron", "多形拟杆菌", 818, "GCF_014131755.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: diarrhea relief, lipid metabolism disorders"),
    ("RLA", "Ruminococcus lactaris", "酸奶瘤胃球菌", 46228, "GCF_025152405.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: ASD behavioral phenotype"),
    ("RCA", "Ruminococcus callidus", "伶俐瘤胃球菌", 40519, "GCF_049562855.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: Crohn's disease, intestinal barrier repair"),
    ("RIN", "Roseburia intestinalis", "肠道罗斯拜瑞氏菌", 166486, "GCF_900537995.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: anti-inflammatory, depression, metabolic diseases"),
    ("ESI", "Eubacterium siraeum", "惰性真杆菌", 39492, "GCF_001404415.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: intestinal mucosal repair, inhibition of fat deposition"),
    ("DWE", "Dysosmobacter welbionis", "威尔伯臭杆菌", 2093857, "GCF_965585535.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: weight control, fatty liver improvement"),
    ("OLA", "Odoribacter laneus", "兰氏臭杆菌", 626933, "GCF_000243215.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: obesity, insulin resistance"),
    ("FPL", "Flavonifractor plautii", "珀氏解黄酮菌", 292800, "GCF_010508875.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: anti-inflammatory, flavonoid metabolism"),
    ("ERA", "Eubacterium ramulus", "细枝真杆菌", 39490, "GCF_001406295.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: anti-inflammatory, flavonoid metabolism"),
    ("BSU", "Bacillus subtilis", "枯草芽孢杆菌", 1423, "GCF_000009045.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: anti-inflammatory, gut microbiota homeostasis"),
    ("CSC", "Clostridium scindens", "裂解梭菌", 29347, "GCF_004295125.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: alleviating intestinal aging"),
    ("LGA", "Lactobacillus gasseri", "加氏乳杆菌", 1596, "GCF_000014425.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: atrial fibrillation prevention"),
    ("ECL", "Enterocloster clostridioformis", "小梭形肠道梭状菌", 1531, "GCF_012273195.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: anti-Salmonella infection"),
    ("CMI", "Christensenella minuta", "小克里斯滕森氏菌", 626937, "GCF_003628755.1", "NCBI RefSeq (GCF),Uniprot", "Research focus: obesity, hyperglycemia, dyslipidemia"),
]

def import_species(conn):
    c = conn.cursor()
    c.executemany("""
        INSERT OR REPLACE INTO Species 
        (Species_ID, Scientific_Name, Chinese_Name, Taxonomy_ID, Genome_Accession, Proteome_Source, Notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, SPECIES_DATA)
    conn.commit()
    print(f"[OK] 菌种导入: {len(SPECIES_DATA)} 条")

def import_csv(conn, filename, table_name, columns):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[跳过] {filename} 不存在")
        return
    c = conn.cursor()
    rows = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get(columns[0]) or "EXAMPLE" in str(row[columns[0]]).upper() or "示例" in str(row.get(columns[0], "")):
                continue
            values = []
            for col in columns:
                val = (row.get(col, "") or "").strip()
                int_cols = ("AA_Length","Full_Length","SignalP_SPLen","Length","Taxonomy_ID","hbonds_int")
                float_cols = ("Raw_Score","DeepLocPro_ExtProb","dG_sep_norm","dSASA_int","complex_norm",
                              "total_score","packstat","pLDDT_total","pLDDT_binder","PAE_interaction",
                              "binder_RMSD","target_RMSD")
                if col in int_cols and val:
                    try: val = int(val)
                    except: pass
                elif col in float_cols and val:
                    try: val = float(val)
                    except: pass
                elif val == "":
                    val = None
                values.append(val)
            rows.append(tuple(values))
    if rows:
        ph = ", ".join(["?"] * len(columns))
        cn = ", ".join(columns)
        c.executemany(f"INSERT OR REPLACE INTO {table_name} ({cn}) VALUES ({ph})", rows)
        conn.commit()
        print(f"[OK] {table_name} 导入 {len(rows)} 条")

def main():
    if not os.path.exists(DB_PATH):
        print("请先运行: python init_db.py")
        return
    conn = sqlite3.connect(DB_PATH)
    import_species(conn)
    import_csv(conn, "proteins.csv", "Target_Protein",
        ["Species_ID","Protein_ID","ID_Accession","Full_Length","Full_Sequence","AA_Length",
         "Design_Region","Protein_Sequence","Localization_Evidence","DeepLocPro_Location",
         "DeepLocPro_ExtProb","SignalP_Category","SignalP_SPLen","DeepTMHMM_Type","Pfam_Family",
         "Notes"])
    import_csv(conn, "binders.csv", "Binder",
        ["Binder_ID","Species_ID","Binder_Sequence","Length","Raw_Score","dG_sep_norm","dSASA_int",
         "complex_norm","total_score","packstat","hbonds_int","pLDDT_total","pLDDT_binder",
         "PAE_interaction","binder_RMSD","target_RMSD","Sequence_File","Structure_File","Notes"])

    c = conn.cursor()
    for t in ["Species", "Target_Protein", "Binder"]:
        n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {n} 条")
    conn.close()

if __name__ == "__main__":
    main()
