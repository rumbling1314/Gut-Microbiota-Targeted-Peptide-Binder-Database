"""
Gut Microbiota Binder Design Database
启动: python app.py  →  浏览器打开 http://127.0.0.1:5000
"""
import sqlite3
import os
import re
from flask import Flask, render_template, g, request

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "binder_db.db")
MD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "md_plots")

# Public GitHub repository URL
REPO_URL = "https://github.com/rumbling1314/Gut-Microbiota-Targeted-Peptide-Binder-Database"

# Database version (semantic versioning, read from the VERSION file)
def _read_version():
    vp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")
    try:
        return open(vp, encoding='utf-8').read().strip()
    except Exception:
        return "0.0.0"
DB_VERSION = _read_version()

@app.context_processor
def inject_meta():
    return {'DB_VERSION': DB_VERSION, 'REPO_URL': REPO_URL}

# Binder/MD 编号 -> Species_ID
NUM2SID = {
    '009':'ANB','014':'RBR','016':'BCR','022':'RCA','023':'RIN','027':'FSA','028':'AHA',
    '029':'PFA','030':'RFA','031':'CEU','032':'BFR','040':'DWE','041':'ARE','043':'BWE',
    '045':'FPR','047':'BSU','051':'FPL','055':'CSC','056':'ECL'}
SID2NUM = {v: k for k, v in NUM2SID.items()}

# MD 8 types of analysis plots (filename prefix, title, description)
PLOT_META = [
    ('rmsd',       'RMSD (Root-Mean-Square Deviation)', 'Overall structural stability of the complex over simulation time'),
    ('rmsf',       'RMSF (Root-Mean-Square Fluctuation)', 'Flexibility and local fluctuations of individual residues'),
    ('rg',         'Rg (Radius of Gyration)',          'Change in the overall compactness of the molecule over time'),
    ('hbond',      'Number of Hydrogen Bonds',         'Hydrogen bonds between the binder and target over time'),
    ('mindist',    'Minimum Distance',                 'Closest distance between the binder and target protein'),
    ('temperature','Temperature',                      'Temperature coupling stability (target ~310 K)'),
    ('pressure',   'Pressure',                         'Pressure coupling stability'),
    ('potential',  'Potential Energy',                 'Potential energy of the system over simulation time'),
]

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db: db.close()

# 首页
@app.route('/')
def index():
    db = get_db()
    s = {}
    s['species'] = db.execute("SELECT COUNT(*) FROM Species").fetchone()[0]
    s['proteins'] = db.execute("SELECT COUNT(*) FROM Target_Protein").fetchone()[0]
    s['binders'] = db.execute("SELECT COUNT(*) FROM Binder").fetchone()[0]
    # 有Binder的菌种数（重点指标）
    s['success_species'] = db.execute("SELECT COUNT(DISTINCT Species_ID) FROM Binder").fetchone()[0]
    # 有Binder的蛋白数
    s['success_proteins'] = db.execute("""
        SELECT COUNT(DISTINCT p.Protein_ID) FROM Target_Protein p
        JOIN Binder b ON p.Species_ID = b.Species_ID
    """).fetchone()[0]

    recent = []
    if s['binders'] > 0:
        recent = db.execute("""
            SELECT b.*, s.Scientific_Name, s.Chinese_Name
            FROM Binder b JOIN Species s ON b.Species_ID = s.Species_ID
            ORDER BY b.Raw_Score ASC LIMIT 10
        """).fetchall()
    # 尚无Binder的待筛选菌种
    pending = db.execute("""
        SELECT Species_ID, Chinese_Name, Scientific_Name FROM Species
        WHERE Species_ID NOT IN (SELECT DISTINCT Species_ID FROM Binder)
        ORDER BY Species_ID
    """).fetchall()
    return render_template('index.html', stats=s, recent=recent, pending=pending)

# 菌种列表
@app.route('/species')
def species_list():
    db = get_db()
    q = request.args.get('q', '')
    if q:
        rows = db.execute("""
            SELECT s.*,
                   (SELECT COUNT(*) FROM Target_Protein p WHERE p.Species_ID=s.Species_ID) as protein_cnt,
                   (SELECT COUNT(*) FROM Binder b WHERE b.Species_ID=s.Species_ID) as binder_cnt
            FROM Species s WHERE s.Scientific_Name LIKE ? OR s.Chinese_Name LIKE ? OR s.Species_ID LIKE ?
            ORDER BY s.Species_ID
        """, (f'%{q}%',f'%{q}%',f'%{q}%')).fetchall()
    else:
        rows = db.execute("""
            SELECT s.*,
                   (SELECT COUNT(*) FROM Target_Protein p WHERE p.Species_ID=s.Species_ID) as protein_cnt,
                   (SELECT COUNT(*) FROM Binder b WHERE b.Species_ID=s.Species_ID) as binder_cnt
            FROM Species s ORDER BY s.Species_ID
        """).fetchall()
    return render_template('species.html', species=rows, q=q)

# 菌种详情
@app.route('/species/<sid>')
def species_detail(sid):
    db = get_db()
    sp = db.execute("SELECT * FROM Species WHERE Species_ID=?", (sid,)).fetchone()
    if not sp: return "未找到", 404
    proteins = db.execute("SELECT * FROM Target_Protein WHERE Species_ID=?", (sid,)).fetchall()
    binders = db.execute("SELECT * FROM Binder WHERE Species_ID=? ORDER BY Raw_Score", (sid,)).fetchall()
    return render_template('species_detail.html', sp=sp, proteins=proteins, binders=binders)

# 蛋白列表
@app.route('/proteins')
def protein_list():
    db = get_db()
    q = request.args.get('q', '')
    sql = """
        SELECT p.*, s.Scientific_Name, s.Chinese_Name,
               (SELECT COUNT(*) FROM Binder b WHERE b.Species_ID=p.Species_ID) as binder_cnt
        FROM Target_Protein p JOIN Species s ON p.Species_ID=s.Species_ID
    """
    if q:
        rows = db.execute(sql+" WHERE p.Protein_ID LIKE ? OR s.Scientific_Name LIKE ? ORDER BY p.Protein_ID",
                          (f'%{q}%',f'%{q}%')).fetchall()
    else:
        rows = db.execute(sql+" ORDER BY p.Protein_ID").fetchall()
    return render_template('proteins.html', proteins=rows, q=q)

# 蛋白详情
@app.route('/proteins/<pid>')
def protein_detail(pid):
    db = get_db()
    p = db.execute("""
        SELECT p.*, s.Scientific_Name, s.Chinese_Name
        FROM Target_Protein p JOIN Species s ON p.Species_ID=s.Species_ID
        WHERE p.Protein_ID=?
    """, (pid,)).fetchone()
    if not p: return "未找到", 404
    binders = db.execute("""
        SELECT * FROM Binder WHERE Species_ID=? ORDER BY Raw_Score
    """, (p['Species_ID'],)).fetchall()
    _num = SID2NUM.get(p['Species_ID'])
    target_pdb = (_num + '_target.pdb') if _num else None
    return render_template('protein_detail.html', p=p, binders=binders, target_pdb=target_pdb)

# Binder列表
@app.route('/binders')
def binder_list():
    db = get_db()
    q = request.args.get('q', '')
    sql = """
        SELECT b.*, s.Scientific_Name, s.Chinese_Name
        FROM Binder b JOIN Species s ON b.Species_ID=s.Species_ID
    """
    if q:
        rows = db.execute(sql+" WHERE b.Binder_ID LIKE ? OR b.Binder_Sequence LIKE ? OR s.Scientific_Name LIKE ? ORDER BY b.Raw_Score LIMIT 200",
                          (f'%{q}%',f'%{q}%',f'%{q}%')).fetchall()
    else:
        rows = db.execute(sql+" ORDER BY b.Raw_Score LIMIT 200").fetchall()
    return render_template('binders.html', binders=rows, q=q)

# Binder详情（含3D PDB查看）
@app.route('/binders/<bid>')
def binder_detail(bid):
    db = get_db()
    b = db.execute("""
        SELECT b.*, s.Scientific_Name, s.Chinese_Name
        FROM Binder b JOIN Species s ON b.Species_ID=s.Species_ID
        WHERE b.Binder_ID=?
    """, (bid,)).fetchone()
    if not b: return "未找到", 404
    return render_template('binder_detail.html', b=b)

# MD图像分析 - 列表
@app.route('/md')
def md_list():
    db = get_db()
    items = []
    if os.path.isdir(MD_DIR):
        for sid in sorted(os.listdir(MD_DIR)):
            sd = os.path.join(MD_DIR, sid)
            if not os.path.isdir(sd):
                continue
            sp = db.execute("SELECT * FROM Species WHERE Species_ID=?", (sid,)).fetchone()
            designs = [x for x in os.listdir(sd) if os.path.isdir(os.path.join(sd, x))]
            total_png = 0
            for d in designs:
                total_png += len([x for x in os.listdir(os.path.join(sd, d)) if x.endswith('.png')])
            items.append({'sid': sid, 'sp': sp, 'designs': len(designs), 'count': total_png})
    return render_template('md.html', items=items)

# MD图像分析 - 某菌种详情（支持多 binder，按 design 分组）
@app.route('/md/<sid>')
def md_detail(sid):
    db = get_db()
    sp = db.execute("SELECT * FROM Species WHERE Species_ID=?", (sid,)).fetchone()
    if not sp:
        return "未找到该菌种", 404
    sd = os.path.join(MD_DIR, sid)
    if not os.path.isdir(sd):
        return "未找到该菌种的MD分析数据", 404
    # 从 Binder 表关联每个 design 的编号、Binder_ID、PDB 文件名
    rows = db.execute(
        "SELECT Binder_ID, Structure_File FROM Binder WHERE Species_ID=? ORDER BY Binder_ID",
        (sid,)).fetchall()
    meta = {}
    for r in rows:
        m = re.match(r"(\d+)_(.+?)_dldesign", r['Structure_File'] or '')
        if m:
            meta[m.group(2)] = (m.group(1), r['Binder_ID'], r['Structure_File'])
    designs = []
    for d in sorted(os.listdir(sd)):
        dd = os.path.join(sd, d)
        if not os.path.isdir(dd):
            continue
        available = {x[:-4] for x in os.listdir(dd) if x.endswith('.png')}
        plots = []
        for key, title, desc in PLOT_META:
            url = ("/static/md_plots/%s/%s/%s.png" % (sid, d, key)) if key in available else None
            plots.append((key, title, desc, url))
        num, bid, sfile = meta.get(d, ('?', '?', '?'))
        designs.append({'design': d, 'num': num, 'binder_id': bid, 'sfile': sfile, 'plots': plots})
    def _porder(item):
        m = re.search(r'P(\d+)$', item['binder_id'])
        return int(m.group(1)) if m else 999
    designs.sort(key=_porder)
    return render_template('md_detail.html', sp=sp, designs=designs)

# About / 简介
@app.route('/about')
def about():
    db = get_db()
    counts = {
        'species':  db.execute("SELECT COUNT(*) FROM Species").fetchone()[0],
        'proteins': db.execute("SELECT COUNT(*) FROM Target_Protein").fetchone()[0],
        'binders':  db.execute("SELECT COUNT(*) FROM Binder").fetchone()[0],
    }
    return render_template('about.html', c=counts,
                           repo_url=REPO_URL, repo_issues=REPO_URL + '/issues')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    print("=" * 50)
    print("  Gut Microbiota Binder Design Database")
    print("  http://127.0.0.1:%d" % port)
    print("=" * 50)
    app.run(debug=debug, host='0.0.0.0', port=port)
