"""
Gut Microbiota Binder Design Database
启动: python app.py  →  浏览器打开 http://127.0.0.1:5000
"""
import sqlite3
import os
from flask import Flask, render_template, g, request

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "binder_db.db")
MD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "md_plots")

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
    return render_template('protein_detail.html', p=p, binders=binders)

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
        for num in sorted(os.listdir(MD_DIR)):
            d = os.path.join(MD_DIR, num)
            if not os.path.isdir(d):
                continue
            sid = NUM2SID.get(num)
            sp = db.execute("SELECT * FROM Species WHERE Species_ID=?", (sid,)).fetchone() if sid else None
            cnt = len([x for x in os.listdir(d) if x.endswith('.png')])
            items.append({'num': num, 'sid': sid, 'sp': sp, 'count': cnt})
    return render_template('md.html', items=items)

# MD图像分析 - 某菌种详情
@app.route('/md/<sid>')
def md_detail(sid):
    num = SID2NUM.get(sid)
    d = os.path.join(MD_DIR, num) if num else ''
    if not num or not os.path.isdir(d):
        return "未找到该菌种的MD分析数据", 404
    db = get_db()
    sp = db.execute("SELECT * FROM Species WHERE Species_ID=?", (sid,)).fetchone()
    available = {x[:-4] for x in os.listdir(d) if x.endswith('.png')}
    plots = [(key, title, desc, key in available) for key, title, desc in PLOT_META]
    return render_template('md_detail.html', sp=sp, num=num, plots=plots)

if __name__ == '__main__':
    print("=" * 50)
    print("  Gut Microbiota Binder Design Database")
    print("  http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
