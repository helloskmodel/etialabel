#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build records_raw.json from fetched FLEXcon pages (automotive/healthcare/electronics only)."""
import re, os, json, glob, html as H

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = "https://www.flexcon.com"

# ---------------- spotlight metadata ----------------
SP = {
 'automotive-product-list': dict(sectors=['AUTOMOTIVE'], cat='Automotive > Flexcon Automotive Product List'),
 'flexcon-nexgen': dict(sectors=['AUTOMOTIVE','ELECTRONICS'], cat='Automotive > Security/Tamper-Evident Labels | Electronics > Brand ID / Warning-Instructional / Security / Compliance-Tracking > Flexcon® NexGen™'),
 'flexcon-thermlfilm-nexgen': dict(sectors=['AUTOMOTIVE'], cat='Automotive > Cable & Wire Labeling / Security/Tamper-Evident Labels > Flexcon® ThermlFilm® NexGen™'),
 'flexcon-dpm': dict(sectors=['AUTOMOTIVE','ELECTRONICS'], cat='Automotive > Security/Tamper-Evident Labels | Electronics > Brand ID / Warning-Instructional / Compliance-Tracking > Flexcon® DPM® EcoFocus®'),
 'dpm-overlaminates': dict(sectors=['AUTOMOTIVE','ELECTRONICS'], cat='Automotive > Security/Tamper-Evident Labels | Electronics > Brand ID / Warning-Instructional > Flexcon Overlaminates'),
 'tampermark': dict(sectors=['AUTOMOTIVE','ELECTRONICS'], cat='Automotive > Security/Tamper-Evident Labels | Electronics > Tamper-Evident Destructible Labels > TamperMark'),
 'silicone-adhesives': dict(sectors=['AUTOMOTIVE','ELECTRONICS'], cat='Automotive > Bonding | Electronics > Mounting / Damping / Gasketing-Sealing / Barrier > Flexcon® SA Series Silicone Adhesives'),
 'flexmount-select-double-faced-adhesives': dict(sectors=['AUTOMOTIVE','ELECTRONICS'], cat='Automotive > Bonding | Electronics > High-Performance Mounting Adhesives > Flexcon Adhesive Transfer Tape and Double-face Tape'),
 'flexcon-flexmount-l-59fr': dict(sectors=['AUTOMOTIVE'], cat='Automotive > Bonding > Flexcon® FlexMount® L-59FR'),
 'tapes-for-gasketing': dict(sectors=['ELECTRONICS'], cat='Electronics > Gasketing and Sealing Adhesives > Tapes for Gasketing'),
 'dermaflex': dict(sectors=['MEDICAL'], cat='Healthcare > Wearables > Flexcon® DermaFlex™'),
 'dermaflex-nnru': dict(sectors=['MEDICAL'], cat='Healthcare > Wearables > Flexcon® DermaFlex™ NNRU'),
 'dermaflex-nwp-long-term-wear': dict(sectors=['MEDICAL'], cat='Healthcare > Wearables > DermaFlex™ NWP Long-Term Wear'),
 'cryoflex': dict(sectors=['MEDICAL'], cat='Healthcare > Pharmaceutical > Flexcon PharmCal® CryoFlex™'),
 'flexcon-omni-wave': dict(sectors=['MEDICAL'], cat='Healthcare > Diagnostics > Flexcon® Omni-Wave™'),
 'flexcon-pharmcal': dict(sectors=['MEDICAL'], cat='Healthcare > Pharmaceutical > Flexcon® PharmCal®'),
 'medflex': dict(sectors=['MEDICAL'], cat='Healthcare > Medical Device > Flexcon® MedFlex®'),
 'pharmcal-biomark': dict(sectors=['MEDICAL'], cat='Healthcare > Pharmaceutical > PharmCal® BioMark'),
}

# product id -> set of spotlight slugs (from extracted links)
LINKS = {
 'automotive-product-list': ['284','303','324','440','464','6068','6234','12547','51249','54109','54111','64392','68768'],
 'cryoflex': ['300','301','302','70806'],
 'dermaflex-nnru': ['6979','68278','69014'],
 'dermaflex-nwp-long-term-wear': ['70246'],
 'dermaflex': ['6979','65697','68278','68292','68293','68635','69014','70246'],
 'dpm-overlaminates': ['303','304','324','360','361','464','12395','69283'],
 'flexcon-dpm': ['70307','70308','70334'],
 'flexcon-flexmount-l-59fr': ['68228','68231','68345','68347','68348','68874','68876','68878','68879'],
 'flexcon-nexgen': ['54103','54108','54109','54110'],
 'flexcon-omni-wave': ['70271'],
 'flexcon-thermlfilm-nexgen': ['55049'],
 'flexmount-select-double-faced-adhesives': ['487','488','562','564','12729','54149'],
 'tampermark': ['443','446','27516'],
}

prod2sp = {}
for sp, ids in LINKS.items():
    for i in ids:
        prod2sp.setdefault(i, []).append(sp)

# pid -> canonical product URL (from links seen on flexcon.com pages)
PRODUCT_URLS = {}
for u in open(f'{BASE}/product_urls.txt').read().split():
    pid = u.split('/products/')[1].split('/')[0]
    PRODUCT_URLS.setdefault(pid, u)

# ---------------- Chinese translation helper ----------------
TOK = [
 ('engineered material for extreme storage conditions','极端储存条件工程标签材料'),
 ('skin contact applications - electrodes & wearables hydrogel-free bio-signal sensing transfer tape','皮肤接触应用-电极与可穿戴设备用无水凝胶生物信号传感转移胶带'),
 ('skin contact applications','皮肤接触应用'),
 ('consumer durables & industrial products','耐用消费品与工业产品用'),
 ('liquid nitrogen','液氮'),('uv resistant','耐UV'),
 ('for bonding and mounting applications','粘接与安装应用'),
 ('nylon reinforced polyurethane','尼龙增强聚氨酯'),('reinforced nylon','增强尼龙'),
 ('nonwoven flesh polyester fabric','无纺肤色聚酯纤维布'),('non-woven polyester','无纺聚酯'),
 ('brushed stainless','拉丝不锈钢面'),('overlaminating','覆膜用'),('overlaminate','覆膜'),('overlam','覆膜'),
 ('transfer tape','转移胶带'),('double faced liner','双面底纸'),('double-faced','双面'),('double faced','双面'),
 ('roll-form liner','卷式底纸'),('roll form liner','卷式底纸'),('film liner','薄膜底纸'),('paper liner','纸底纸'),
 ('bleached kraft','漂白牛皮纸'),('kraft','牛皮纸'),('liner','底纸'),
 ('high-performance with fluoresce','高性能含荧光示踪'),('high-performance','高性能'),('high performance','高性能'),
 ('general purpose','通用型'),('permanent adhesive','永久胶'),('removable adhesive','可移除胶'),
 ('permanent','永久型'),('removable','可移除'),('adhesive','胶粘剂'),
 ('gloss topcoated','光面涂层'),('matte topcoated','哑面涂层'),('topcoated','面涂层'),('topcoat','面涂层'),
 ('ultra low deep freeze','超低温深冻'),('deep freeze','深冻'),('cryogenic','低温冷冻'),
 ('white matte','哑白色'),('clear matte','哑光透明'),('white opaque gloss','高遮盖亮白'),('white opaque matte','高遮盖哑白'),
 ('white gloss','亮白色'),('satin white','缎面白'),('satin silver','缎面银'),('silver matte','哑面银'),('silv mat','哑面银'),
 ('silver void','银色VOID防揭'),('white void','白色VOID防揭'),('void','VOID防揭'),
 ('checkerboard pattern','棋盘格防揭图案'),('checkerboard','棋盘格'),
 ('surface destruct','表面破坏型'),('film destruct','膜层破坏型'),('destruct','破坏型'),
 ('polyester','聚酯(PET)'),('polypropylene','聚丙烯(PP)'),('polyethylene','聚乙烯(PE)'),
 ('polyimide','聚酰亚胺(PI)'),('polyolefin','聚烯烃'),('polycarbonate','聚碳酸酯(PC)'),('vinyl','乙烯基(PVC)'),
 ('aluminum foil','铝箔'),('foil','箔'),
 ('piggyback','背贴式(Piggyback)'),('single-ply','单层'),
 ('flame-retardant','阻燃'),('self-extinguishing','自熄型'),
 ('uv ','UV '),('clear','透明'),('white','白色'),('silver','银色'),('yellow','黄色'),('black','黑色'),
 ('flesh','肤色'),('amber','琥珀色'),('velvet','丝绒面'),('gloss','光面'),('matte','哑光'),
 ('mil','密尔'),('mils','密尔'),
 ('pattern','图案'),
 ('durable goods and equipment labeling','耐用品与设备标签'),
 ('roll form laminating','卷式复合'),('aerospace','航空航天'),
 ('automotive engine compartment cover label','汽车发动机舱盖标签'),
 ('nameplate / decorativew','铭牌/装饰'),('nameplate','铭牌'),('decorative','装饰'),
 ('engineered materials for extreme storage conditions','极端储存条件工程标签材料'),
 ('labeling','标签'),('label','标签'),('applications','应用'),('application','应用'),
 ('nonwoven','无纺'),('fabric','纤维布'),('poly ','聚酯膜 '),('film','薄膜'),
 ('thermal transfer printable','热转印可打印'),('security / authenticity','安全/防伪'),
 ('destructible','可破坏型'),('permanant','永久型'),('skin contact','皮肤接触'),
 ('foam','泡棉'),('high temp','耐高温'),
 ('with','配'),('and','和'),
]
def cn(text):
    t = ' ' + text + ' '
    for en, zh in TOK:
        t = re.sub(r'(?i)(?<![a-z])' + re.escape(en) + r'(?![a-z])', zh, t)
    t = re.sub(r'\s+', ' ', t).strip(' ,')
    return t

# ---------------- parse product detail pages ----------------
KEYS = ['Adhesive','Product Agency','Color Family','Converting','Film Family','Master Web Width',
        'Other Available Widths','Print Technology','Surface Type','Surface Treatment','Surface Texture','Surface Profile']

def parse_prod(pid):
    txt = open(f'{BASE}/html/prod_{pid}.txt').read().split('\n')
    raw = open(f'{BASE}/html/prod_{pid}.html').read()
    d = {'pid': pid}
    m = re.search(r'href="(/products-pdf/[^"]+)"', raw)
    d['tds'] = SITE + m.group(1) if m else ''
    d['url'] = PRODUCT_URLS.get(pid, '')
    # header block after last 'Search for anything'
    idx = max(i for i, l in enumerate(txt) if l == 'Search for anything')
    i = idx + 1
    d['flx'] = txt[i]; i += 1
    d['part'] = ''
    if txt[i].startswith('Part #'):
        d['part'] = txt[i]; i += 1
    d['title'] = txt[i]; i += 1
    d['subtitle'] = txt[i] if txt[i] != 'Request information' else ''
    def section(start, stops):
        try: s = txt.index(start, idx)
        except ValueError: return []
        out = []
        for l in txt[s+1:]:
            if l in stops: break
            out.append(l)
        return out
    d['benefits'] = [l for l in section('Benefits', ['Click to view PDF','Features']) if len(l) > 3]
    feats = section('Features', ['Additional Details','Technical Data','Learn more about','Product Details'])
    d['features'] = [l for l in feats if len(l) > 3 and not l.startswith('Learn more')]
    d['details_extra'] = section('Additional Details', ['Technical Data','Product Details'])
    # thickness
    th = []
    try:
        s = txt.index('Thickness (Mils [microns])', idx)
        lines = []
        for l in txt[s+1:]:
            if l.startswith('Test Method') or l == 'Dimensional Stability (%)': break
            lines.append(l)
        lab = None; vals = []
        for l in lines:
            if l in ('Mils','Microns'): continue
            if l in ('Total Product','Film','Adhesive','Liner','Liner 2','Carrier','Adhesive 2'):
                if lab: th.append((lab, vals))
                lab = l; vals = []
            else:
                vals.append(l)
        if lab: th.append((lab, vals))
    except ValueError:
        pass
    d['thickness'] = '; '.join(f"{k} {v[0]} mil" + (f" ({v[1]} µm)" if len(v) > 1 else '') for k, v in th if v)
    # temps (value line must look like a temperature)
    def after(label):
        try:
            j = txt.index(label, idx)
            v = txt[j+1]
            return v if (re.search(r'\d', v) and ('°' in v or 'F' in v or 'C' in v)) else ''
        except ValueError:
            return ''
    st = after('Service Temperature')
    mat = after('Minimum Application Temperature')
    d['temp'] = st + (f"; Min. application temp {mat}" if mat else '')
    # product details table
    pd = {}
    try:
        s = txt.index('Product Details', idx)
        j = s + 1
        if txt[j] == 'Title': j += 1
        if txt[j] == 'Description': j += 1
        while j < len(txt) and not txt[j].startswith('Product Performance'):
            if txt[j] in KEYS:
                val = txt[j+1] if j+1 < len(txt) and txt[j+1] not in KEYS and not txt[j+1].startswith('Product Performance') else ''
                pd[txt[j]] = val
                j += 2 if val else 1
            else:
                j += 1
    except ValueError:
        pass
    d['pd'] = pd
    return d

# helper pick from feature lines
def pick(lines, must, block=()):
    for l in lines:
        low = l.lower()
        if all(m in low for m in must) and not any(b in low for b in block):
            return l
    return ''

CERT_PAT = re.compile(r'\bUL\b|\bcUL\b|\bCSA\b|\bREACH\b|RoHS|ISO[- ]?10993|21 CFR|\bFDA\b|\bAAMI\b|ISEGA|FMVSS|FAR 25|ATEX|IEC 60601|UL_|CUL_|CSA_')

def build_from_detail(pid):
    d = parse_prod(pid)
    feats = d['features']; bens = d['benefits']
    alll = feats + bens + d['details_extra']
    face = pick(feats, ['mil'], ('liner','adhesive'))
    adh = pick(alll, ['adhesive'], ('liner',)) or ''
    pda = d['pd'].get('Adhesive', '')
    if pda and pda != 'N/A' and pda.lower() not in adh.lower():
        adh = (adh + ' | ' if adh else '') + pda
    liner = pick(feats, ['liner']) or pick(bens, ['liner'])
    chem = pick(alll, ['chemical'])
    certs = []
    pa = d['pd'].get('Product Agency', '')
    for l in alll + ([pa] if pa and pa != 'N/A' else []):
        if l and len(l) < 250 and CERT_PAT.search(l) and l not in certs:
            certs.append(l)
    cert = ' | '.join(certs)
    sps = prod2sp.get(pid, [])
    sectors = sorted({s for sp in sps for s in SP[sp]['sectors']})
    cats = ' || '.join(SP[sp]['cat'] for sp in sps)
    app = d['subtitle']
    if d['pd'].get('Surface Type'):
        app += ('; ' if app else '') + 'Surfaces: ' + d['pd']['Surface Type']
    model = d['title']
    rec = {
        'model': model,
        'name_en': (d['title'] + (' – ' + d['subtitle'] if d['subtitle'] else '')),
        'name_cn': cn(d['subtitle']) if d['subtitle'] else cn(d['title']),
        'facestock_raw': face,
        'adhesive_raw': adh,
        'liner': liner,
        'thickness_raw': d['thickness'],
        'temp_raw': d['temp'],
        'chem_raw': chem,
        'sectors': sectors,
        'cert': cert,
        'features': feats,
        'benefits': bens,
        'app_desc': app,
        'source_category_raw': cats,
        'url': d['url'],
        'tds': d['tds'],
        '_flx': d['flx'],
        '_part': d['part'],
    }
    return rec

# ---------------- main ----------------
records = {}
order = []

# product pages that return soft-404 (linked on spotlights but page missing)
MISSING = {'68293','68347','68348','68874','68876','68878'}

detail_ids = sorted([re.search(r'prod_(\d+)\.txt', p).group(1) for p in glob.glob(f'{BASE}/html/prod_*.txt')], key=int)
for pid in detail_ids:
    if pid in MISSING:
        continue
    r = build_from_detail(pid)
    records[pid] = r
    order.append(pid)

# --- records for the 6 dead product pages, built from spotlight page content
L59_URL = SITE + '/spotlights/flexcon-flexmount-l-59fr'
L59_CAT = SP['flexcon-flexmount-l-59fr']['cat']
L59_FILM_CERT = ('UL-recognized; FlexMark® L-59FR products coated at 2.0 mil to 4.0 mil adhesive thickness are rated UL 94 V-0 when coated on 2.0 mil polyimide and 2.0 mil aluminum foil; '
                 'FlexMark® L-59FR products (2.0 mil polyimide & 2.0 mil foil) at a 2.0 mil adhesive thickness meet FMVSS 302; '
                 'at 2.0 mil adhesive thickness pass FAR 25.853 (a) App. F Part I vertical 60/12 sec burn, FAR 25.853 (d) App. F Part IV Heat Release, Part V Smoke Density; BSS 7239 Toxicity Test')
L59_TT_CERT = ('UL-recognized; FlexMount® L-59FR products coated at 2.0 mil to 4.0 mil adhesive thickness are rated UL 94 V-0 when coated on 2.0 mil polyimide and 2.0 mil aluminum foil')
L59_FEATS = ['Excellent Adhesion — high-performance adhesion to a wide range of surfaces within aircrafts and motor vehicles',
             'Two Adhesive Thicknesses – suitable for smooth or rough textured surfaces',
             'Self-Extinguishing – meets UL 94 standards']
L59_APP = ('Mounting & bonding in transportation; FMVSS-suitable automotive applications: seat cushions, seat belts, headlining, convertible tops, armrests, trim panels, '
           'compartment shelves, head restraints, sun visors, shades, wheel housing covers, engine compartment covers, floor coverings; plus FAR-compliant aerospace interiors')
def l59(flx, model, name_cn, face, thick, cert):
    key = 'l59_' + flx
    records[key] = {
        'model': model, 'name_en': model, 'name_cn': name_cn,
        'facestock_raw': face,
        'adhesive_raw': 'V-59FR self-extinguishing flame-retardant adhesive (L-59FR series)',
        'liner': '', 'thickness_raw': thick, 'temp_raw': '', 'chem_raw': '',
        'sectors': ['AUTOMOTIVE'], 'cert': cert,
        'features': L59_FEATS, 'benefits': [],
        'app_desc': L59_APP,
        'source_category_raw': L59_CAT, 'url': L59_URL, 'tds': '',
        '_flx': 'FLX' + flx, '_part': '',
    }
    order.append(key)

l59('068347','FlexMark® L-59FR 068347 (2.0 mil polyimide, 2.0 mil adhesive)','FlexMark® L-59FR 068347 阻燃涂胶膜(2.0密尔聚酰亚胺,2.0密尔胶层)','2.0 mil polyimide','2.0 mil polyimide film, 2.0 mil adhesive',L59_FILM_CERT)
l59('068876','FlexMark® L-59FR 068876 (2.0 mil polyimide, 4.0 mil adhesive)','FlexMark® L-59FR 068876 阻燃涂胶膜(2.0密尔聚酰亚胺,4.0密尔胶层)','2.0 mil polyimide','2.0 mil polyimide film, 4.0 mil adhesive',L59_FILM_CERT)
l59('068348','FlexMark® L-59FR 068348 (2.0 mil foil, 2.0 mil adhesive)','FlexMark® L-59FR 068348 阻燃涂胶铝箔(2.0密尔铝箔,2.0密尔胶层)','2.0 mil aluminum foil','2.0 mil foil, 2.0 mil adhesive',L59_FILM_CERT)
l59('068878','FlexMark® L-59FR 068878 (2.0 mil foil, 4.0 mil adhesive)','FlexMark® L-59FR 068878 阻燃涂胶铝箔(2.0密尔铝箔,4.0密尔胶层)','2.0 mil aluminum foil','2.0 mil foil, 4.0 mil adhesive',L59_FILM_CERT)
l59('068874','FlexMount® L-59FR 068874 (4.0 mil transfer tape, 84# liner)','FlexMount® L-59FR 068874 阻燃转移胶带(4.0密尔,84#底纸)','','4.0 mil transfer tape; 84# liner',L59_TT_CERT)

records['df_68293'] = {
    'model': 'DermaFlex™ P.E.F. 32 WHITE H-778 90 PFW (1.9-2.1)',
    'name_en': 'DermaFlex™ P.E.F. 32 WHITE H-778 90 PFW (1.9-2.1) – soft foam substrate for bio-signal electrode components',
    'name_cn': 'DermaFlex™ P.E.F. 32 白色软质泡棉电极基材,H-778皮肤接触胶',
    'facestock_raw': 'P.E.F. soft foam substrate (Foam (P.E.F.))',
    'adhesive_raw': 'H-778 skin-friendly medical adhesive (tested for biocompatibility - skin irritation, sensitization, and cytotoxicity - using ISO-10993 or similar test methods)',
    'liner': '', 'thickness_raw': '', 'temp_raw': '', 'chem_raw': '',
    'sectors': ['MEDICAL'],
    'cert': 'Adhesive tested for biocompatibility per ISO-10993 or similar test methods (H-778 Biocompatibility Letter available)',
    'features': ['Soft foam substrate for ECG, EMG, EEG electrodes','Flexible and breathable substrate'],
    'benefits': ['Medical grade adhesives developed with patient comfort in mind'],
    'app_desc': 'Bio-signal electrode components: ECG electrodes, EMG electrodes, EEG electrodes',
    'source_category_raw': SP['dermaflex']['cat'],
    'url': SITE + '/spotlights/dermaflex', 'tds': '',
    '_flx': 'FLX068293', '_part': '',
}
order.append('df_68293')

# --- automotive product list table: add category info / create table-only records
auto = json.load(open(f'{BASE}/auto_tables.json'))
AUTO_URL = SITE + '/spotlights/automotive-product-list'
for t in auto:
    cat = 'Automotive > Flexcon Automotive Product List > ' + t['cat']
    for row in t['rows'][1:]:
        c = row['cells']
        if len(c) == 8:
            flx, part, name, adhesive, topcoat, film, color, temp = c
        elif len(c) == 7:
            flx, name, adhesive, topcoat, film, color, temp = c; part = ''
            if re.match(r'^[A-Z]{2,4}-', flx):  # part number in first cell, no FLX
                part = flx; flx = ''
        else:
            continue
        pid = row['pid'] or (flx.strip('*').lstrip('0') if flx else None)
        if pid and pid in records:
            r = records[pid]
            if 'AUTOMOTIVE' not in r['sectors']:
                r['sectors'] = sorted(set(r['sectors'] + ['AUTOMOTIVE']))
            r['source_category_raw'] = (r['source_category_raw'] + ' || ' if r['source_category_raw'] else '') + cat
            continue
        key = 'auto_' + (flx or part)
        if key in records:  # same FLX in two categories
            records[key]['source_category_raw'] += ' || ' + cat
            continue
        records[key] = {
            'model': name,
            'name_en': name,
            'name_cn': cn(name),
            'facestock_raw': film,
            'adhesive_raw': adhesive,
            'liner': '',
            'thickness_raw': '',
            'temp_raw': temp,
            'chem_raw': '',
            'sectors': ['AUTOMOTIVE'],
            'cert': '',
            'features': ([f'Topcoat: {topcoat}'] if topcoat else []) + ([f'Color: {color}'] if color else []),
            'benefits': [],
            'app_desc': t['cat'] + ' (automotive)',
            'source_category_raw': cat,
            'url': AUTO_URL,
            'tds': '',
            '_flx': ('FLX' + flx.strip('*')) if flx else '',
            '_part': ('Part # ' + part) if part else '',
        }
        order.append(key)

# --- flexmount table rows without detail pages (054150, 000491) and gasketing 000546
FM_URL = SITE + '/spotlights/flexmount-select-double-faced-adhesives'
FM_CAT = SP['flexmount-select-double-faced-adhesives']['cat']
for flx, name, film, adhesive, liner in [
    ('054150', 'Flexcon® 2201SL DLC-503-80RH', 'Reinforced Nylon', 'SA 3000 / V-246', '200 Poly FSR MT/78K Coated 2-sided Silicone'),
    ('000491', 'FlexMount® TT 400 L-606 60 LA PFW', 'TT', 'L-606', '60 LA PFW'),
]:
    key = 'fm_' + flx
    records[key] = {
        'model': name, 'name_en': name, 'name_cn': cn(name),
        'facestock_raw': film, 'adhesive_raw': adhesive, 'liner': liner,
        'thickness_raw': '', 'temp_raw': '', 'chem_raw': '',
        'sectors': ['AUTOMOTIVE', 'ELECTRONICS'], 'cert': '',
        'features': [], 'benefits': [],
        'app_desc': 'Transfer and Double-face Tape for bonding and mounting',
        'source_category_raw': FM_CAT, 'url': FM_URL, 'tds': '',
        '_flx': 'FLX' + flx, '_part': '',
    }
    order.append(key)

records['gask_000546'] = {
    'model': 'Flexcon® Select™ DF051521',
    'name_en': 'Flexcon® Select™ DF051521 Clear 0.5 mil Poly Permanent/Permanent Adhesive/Double Faced Liner',
    'name_cn': cn('Clear 0.5 mil Poly Permanent/Permanent Adhesive/Double Faced Liner'),
    'facestock_raw': '0.5 mil Poly', 'adhesive_raw': 'Permanent/Permanent Adhesive',
    'liner': 'Double Faced Liner', 'thickness_raw': '0.5 mil Poly carrier', 'temp_raw': '', 'chem_raw': '',
    'sectors': ['ELECTRONICS'], 'cert': '',
    'features': ['2-Side Pressure-Sensitive Spacer', 'Master Roll Width 60"'], 'benefits': [],
    'app_desc': 'Gasket fabrication - 2-side pressure-sensitive spacer',
    'source_category_raw': SP['tapes-for-gasketing']['cat'],
    'url': SITE + '/spotlights/tapes-for-gasketing', 'tds': '',
    '_flx': 'FLX000546', '_part': '',
}
order.append('gask_000546')

# --- SA Series silicone adhesives family record (no individual product numbers published)
records['sa_series'] = {
    'model': 'Flexcon® SA Series Silicone Adhesives',
    'name_en': 'Flexcon® SA Series Silicone Adhesives – silicone adhesive transfer, single and double-coated tapes',
    'name_cn': 'Flexcon® SA系列有机硅胶粘剂(转移胶带、单面及双面涂布胶带)',
    'facestock_raw': '',
    'adhesive_raw': 'Silicone-based adhesives; available as single- and double-coated tapes, transfer adhesives, and full label constructions',
    'liner': '', 'thickness_raw': '',
    'temp_raw': 'Certain types can tolerate sustained temperature extremes from -300°F to 500°F. Some can even go as high as 800°F to 1000°F for limited periods.',
    'chem_raw': '',
    'sectors': ['AUTOMOTIVE', 'ELECTRONICS'], 'cert': '',
    'features': [
        'Bond to metals, glass, plastics, and elastomers',
        'Single-sided silicone tapes make excellent low-tack protection films for electronic screens',
        'Flexcon® SA1000 Series products offer superior adhesion and wet out for ultra clear application to smooth surfaces, while providing consistent, clean, and quiet removability',
        'High-tack silicone adhesives bond quickly to silicone foam & rubber as well as low surface energy plastics',
    ],
    'benefits': [
        'High-temperature bonding & labeling',
        'Great electrical insulation; guard against moisture, vibration, and temperature changes',
        'Sound and vibration damping in brake pads, hard drives and motor mounts',
    ],
    'app_desc': 'Siliconized surface labeling, high-temp masking, screen protection, assembly, sound & vibration damping; electronics assembly, automotive components, aerospace systems, medical devices, industrial gasketing',
    'source_category_raw': SP['silicone-adhesives']['cat'],
    'url': SITE + '/spotlights/silicone-adhesives', 'tds': '',
    '_flx': '', '_part': '',
}
order.append('sa_series')

# ---------------- records from PDFs (PharmCal families + MedFlex) ----------------
PHARM_URL = SITE + '/spotlights/flexcon-pharmcal'
PHARM_PDF = 'https://assets-us-01.kc-usercontent.com/5ebad2e9-8f0a-0050-6e0b-25e9f568a492/62854f5a-4c75-48fd-8ae6-9c17a5b7b604/Flexcon%20Pharmaceutical%20Labeling%20Solutions.pdf'
MEDFLEX_URL = SITE + '/spotlights/medflex'
MEDFLEX_PDF = 'https://assets-us-01.kc-usercontent.com/5ebad2e9-8f0a-0050-6e0b-25e9f568a492/517b8811-61fd-4a23-9eb5-1a910fb24841/Flexcon%20MedFlex%20products.pdf'

def pharm(flx, family, desc, face, liner, temp, cert, feats, app, name_cn):
    key = 'pharm_' + flx
    records[key] = {
        'model': f'PharmCal® {family} FLX{flx}',
        'name_en': f'PharmCal® {family} – {desc}',
        'name_cn': name_cn,
        'facestock_raw': face,
        'adhesive_raw': ADH.get((family, flx), ADH.get((family, ''), '')),
        'liner': liner,
        'thickness_raw': '',
        'temp_raw': temp,
        'chem_raw': CHEM.get(family, ''),
        'sectors': ['MEDICAL'],
        'cert': cert,
        'features': feats,
        'benefits': BEN.get(family, []),
        'app_desc': app,
        'source_category_raw': f'Healthcare > Pharmaceutical > Flexcon® PharmCal® > PharmCal® {family}',
        'url': PHARM_URL,
        'tds': PHARM_PDF,
        '_flx': 'FLX' + flx, '_part': '',
    }
    order.append(key)

ADH = {
 ('OTC',''): 'High initial tack and strong peel adhesion on plastic packaging',
 ('Supreme',''): 'High-performance adhesives prevent lifting and flagging',
 ('Supreme','000211'): 'High-performance with Fluoresce (fluorescing adhesive)',
 ('TamperMark™',''): 'Sticks firmly to plastic, cardboard, and other packaging materials; specially formulated pressure-sensitive adhesives',
 ('Conceal™',''): 'High-performance; sticks firmly to curved glass or plastic; formulated to reduce the risk of migration through packaging',
 ('BioMark',''): 'Provide strong stickiness, resist chemicals, and bond well to many surfaces (single-ply and piggyback blood bag labels)',
}
CHEM = {
 'Supreme': 'Ensure long-term readability with chemical and abrasion resistance',
 'BioMark': 'Resist chemicals; handles extreme temperature cycling and water submersion',
}
BEN = {
 'OTC': ['Exceptional print surface for precision printing and vibrant detail','Flexible, conformable films wrap smoothly around curved containers','Bleached kraft liner allows back-side registration mark printing for accurate auto-dispensing'],
 'Supreme': ['Wraps smoothly around small, curved containers','Clear film gives a clean, no-label look','Sterilization compatible','Two-year storage stability','Polyester liner ideal for labeling in clean room settings'],
 'TamperMark™': ['Built-in tamper-evident features reveal visible signs of tampering like VOID or checkerboard patterns, or label destruction','Film structure designed to destruct by tearing the package upon removal, prevent reuse or relabeling'],
 'Conceal™': ['Covers existing labels with high-opacity film','Thermal transfer printable topcoat offered in matte or gloss','Matte coating allows easy pen writing'],
 'BioMark': ['Passes hemolysis, cytotoxicity, and irritation testing','Passes centrifuge process','Peel-away top surface liner allows second label use (piggyback)','Handles extreme temperature cycling and water submersion'],
}

OTC_CERT = 'Meets 21 CFR 175.105, REACH, and RoHS/WEE'
otc_temp = 'Wide service temperature range from -40ºF to 212ºF (-40ºC to 100ºC)'
pharm('068902','OTC','2.0 mil Clear Polypropylene, General Purpose, Film Liner','2.0 mil Clear Polypropylene','1.2 mil Clear Polyester film liner',otc_temp,OTC_CERT,['Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable','High-speed auto-dispensing and matrix stripping','Exceptional die cutting'],'Over-the-counter pharmaceutical labeling (large diameter pill containers)','PharmCal® OTC 2.0密尔透明聚丙烯(PP)非处方药标签材料,通用型,薄膜底纸')
pharm('068904','OTC','2.0 mil Clear Polypropylene, General Purpose, Paper Liner','2.0 mil Clear Polypropylene','2.5 mil White Kraft Paper liner',otc_temp,OTC_CERT,['Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable','Thermal printer label sensing','High-speed auto-dispensing and matrix stripping','Good die cutting'],'Over-the-counter pharmaceutical labeling (large diameter pill containers)','PharmCal® OTC 2.0密尔透明聚丙烯(PP)非处方药标签材料,通用型,纸底纸')
pharm('068903','OTC','2.3 mil White Polypropylene, General Purpose, Film Liner','2.3 mil White Polypropylene','1.2 mil Clear Polyester film liner',otc_temp,OTC_CERT,['Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable','High-speed auto-dispensing and matrix stripping','Exceptional die cutting'],'Over-the-counter pharmaceutical labeling (large diameter pill containers)','PharmCal® OTC 2.3密尔白色聚丙烯(PP)非处方药标签材料,通用型,薄膜底纸')
pharm('068905','OTC','2.3 mil White Polypropylene, General Purpose, Paper Liner','2.3 mil White Polypropylene','2.5 mil White Kraft Paper liner',otc_temp,OTC_CERT,['Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable','Thermal printer label sensing','High-speed auto-dispensing and matrix stripping','Good die cutting'],'Over-the-counter pharmaceutical labeling (large diameter pill containers)','PharmCal® OTC 2.3密尔白色聚丙烯(PP)非处方药标签材料,通用型,纸底纸')

SUP_CERT = 'Adhesive tested to ISO 10993-5, -10'
pharm('069045','Supreme','1.5 mil Clear Polyester, High-performance, Film Liner','1.5 mil Clear Polyester','Film liner (clear polyester)','',SUP_CERT,['Adheres to glass and PP: COP, COC','Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable','High-speed auto-dispensing and matrix stripping','Exceptional die cutting; excellent on-press registration'],'Small diameter pharmaceutical labeling – vials, syringes, and ampules','PharmCal® Supreme 1.5密尔透明聚酯(PET)小口径药瓶标签材料,高性能,薄膜底纸')
pharm('000211','Supreme','2.0 mil Clear Polypropylene, High-performance with Fluoresce, Film Liner','2.0 mil Clear Polypropylene','Film liner','',SUP_CERT + '; fluorescing adhesive',['Adheres to glass and PP: COP, COC','Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable','High-speed auto-dispensing and matrix stripping','Exceptional die cutting; excellent on-press registration'],'Small diameter pharmaceutical labeling – vials, syringes, and ampules','PharmCal® Supreme 2.0密尔透明聚丙烯(PP)小口径药瓶标签材料,高性能含荧光示踪胶,薄膜底纸')
pharm('052434','Supreme','2.0 mil Clear Polypropylene, High-performance, Film Liner','2.0 mil Clear Polypropylene','Film liner','',SUP_CERT,['Adheres to glass and PP: COP, COC','Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable','High-speed auto-dispensing and matrix stripping','Exceptional die cutting; excellent on-press registration'],'Small diameter pharmaceutical labeling – vials, syringes, and ampules','PharmCal® Supreme 2.0密尔透明聚丙烯(PP)小口径药瓶标签材料,高性能,薄膜底纸')
pharm('011974','Supreme','2.3 mil White Polypropylene, High-performance, Film Liner','2.3 mil White Polypropylene','Film liner','',SUP_CERT,['Adheres to glass and PP: COP, COC','Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable','High-speed auto-dispensing and matrix stripping','Exceptional die cutting; excellent on-press registration'],'Small diameter pharmaceutical labeling – vials, syringes, and ampules','PharmCal® Supreme 2.3密尔白色聚丙烯(PP)小口径药瓶标签材料,高性能,薄膜底纸')
pharm('068639','Supreme','2.6 mil White Polypropylene, High-performance, Film Liner','2.6 mil White Polypropylene','Film liner','',SUP_CERT,['Adheres to glass and PP: COP, COC','Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable','High-speed auto-dispensing and matrix stripping','Exceptional die cutting; excellent on-press registration'],'Small diameter pharmaceutical labeling – vials, syringes, and ampules','PharmCal® Supreme 2.6密尔白色聚丙烯(PP)小口径药瓶标签材料,高性能,薄膜底纸')

TM_CERT = 'Meets FDA 21 CFR 211.132 and EU FMD regulations'
pharm('006126','TamperMark™','2.0 mil Clear Polypropylene, Surface Destruct, Film Liner','2.0 mil Clear Polypropylene, Surface Destruct','Film liner','',TM_CERT,['Tears cardboard surface','Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable'],'Tamper-evident pharmaceutical labeling – pill containers and boxes','PharmCal® TamperMark™ 2.0密尔透明聚丙烯(PP)表面破坏型防拆标签材料,薄膜底纸')
pharm('069087','TamperMark™','2.0 mil Clear Diacetate, Film Destruct, Paper Liner','2.0 mil Clear Diacetate, Film Destruct','Paper liner','',TM_CERT,['Destructs / prevents relabeling; tears cardboard surface','Conventional printable; thermal printer label sensing','Quilon® coated liner prevents pick off'],'Tamper-evident pharmaceutical labeling – pill containers and boxes','PharmCal® TamperMark™ 2.0密尔透明二醋酸酯膜层破坏型防拆标签材料,纸底纸')
pharm('069051','TamperMark™','2.0 mil White Polyethylene, Film Destruct, Paper Liner','2.0 mil White Polyethylene, Film Destruct','Paper liner','',TM_CERT,['Destructs / prevents relabeling; tears cardboard surface','Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable','Thermal printer label sensing; Quilon® coated liner prevents pick off'],'Tamper-evident pharmaceutical labeling – pill containers and boxes','PharmCal® TamperMark™ 2.0密尔白色聚乙烯(PE)膜层破坏型防拆标签材料,纸底纸')
pharm('069052','TamperMark™','2.0 mil White Polyester, Visible VOID Pattern, Paper Liner','2.0 mil White Polyester, Visible VOID Pattern','Paper liner','',TM_CERT,['Leaves visible evidence (VOID pattern)','Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable','Thermal printer label sensing; Quilon® coated liner prevents pick off'],'Tamper-evident pharmaceutical labeling – pill containers and boxes','PharmCal® TamperMark™ 2.0密尔白色聚酯(PET) VOID防揭图案防拆标签材料,纸底纸')
pharm('069053','TamperMark™','1.5 mil Silver Polyester, Visible Checkerboard Pattern, Paper Liner','1.5 mil Silver Polyester, Visible Checkerboard Pattern','Paper liner','',TM_CERT,['Leaves visible evidence (checkerboard pattern)','Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable','Thermal printer label sensing; Quilon® coated liner prevents pick off'],'Tamper-evident pharmaceutical labeling – pill containers and boxes','PharmCal® TamperMark™ 1.5密尔银色聚酯(PET)棋盘格防揭图案防拆标签材料,纸底纸')

CON_CERT = 'Meets 21 CFR 175.105, REACH, and RoHS/WEE'
con_temp = 'Wide service temperature range from -40ºF to 212ºF (-40ºC to 100ºC)'
pharm('069047','Conceal™','2.3 mil White Opaque Gloss Polypropylene, High-performance, Paper Liner','2.3 mil White Opaque Gloss Polypropylene','Paper liner',con_temp,CON_CERT,['Covers existing markings for relabeling and clinical trials','Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable','Thermal printer label sensing; high-speed auto-dispensing; good die cutting'],'Cover-up labeling for pharma packaging (relabeling, clinical trials)','PharmCal® Conceal™ 2.3密尔高遮盖亮白聚丙烯(PP)遮盖标签材料,高性能,纸底纸')
pharm('069048','Conceal™','2.3 mil White Opaque Matte Polypropylene, High-performance, Paper Liner','2.3 mil White Opaque Matte Polypropylene','Paper liner',con_temp,CON_CERT,['Covers existing markings for relabeling and clinical trials','Accepts pen and marker','Conventional, narrow-format UV inkjet, resin or wax/resin thermal transfer printable','Thermal printer label sensing; high-speed auto-dispensing; good die cutting'],'Cover-up labeling for pharma packaging (relabeling, clinical trials)','PharmCal® Conceal™ 2.3密尔高遮盖哑白聚丙烯(PP)遮盖标签材料,高性能,纸底纸')

BM_CERT = 'Certified by ISEGA; adhesive passes ISO 10993-5, -23 (container side)'
bm_temp = 'Service Temperature -112ºF (-80ºC); engineered to perform from -40°F to 176°F (-40°C to 80°C)'
pharm('069165','BioMark','Piggyback, 3.0 Mil White Polypropylene','3.0 mil White Polypropylene (piggyback construction)','Peel-away top surface liner allows second label use',bm_temp,BM_CERT,['Piggyback construction for blood and plasma bag asset tracking','Conventional, resin or wax/resin thermal transfer printable'],'Blood bag and plasma bag labeling – primary and secondary asset tracking','PharmCal® BioMark 背贴式(Piggyback) 3.0密尔白色聚丙烯(PP)血袋标签材料')
pharm('069088','BioMark','3.8 mil White Matte Polyethylene, Permanent, Paper Liner','3.8 mil White Matte Polyethylene','Paper liner',bm_temp,BM_CERT,['Single-ply construction prints and applies directly to packaging','Conventional, resin or wax/resin thermal transfer printable'],'Blood bag and plasma bag labeling – primary and secondary asset tracking','PharmCal® BioMark 单层3.8密尔哑白聚乙烯(PE)永久型血袋标签材料,纸底纸')

# MedFlex products (from Flexcon MedFlex products PDF + medflex spotlight)
MF_FILM_CERT = 'UL Recognized; UL Verified (V487460) with 6 additional cleaning agents; compliant with IEC 60601-1 3rd edition for marking durability rub tests; meets IEC 60601-1 3rd edition standards'
MF_OL_CERT = 'UL-recognized; compliant with IEC 60601-1 3rd edition for marking durability rub tests'
MF_FILM_ADH = 'Permanent solvent-based acrylic biocompatible adhesive'
MF_OL_ADH = 'Permanent solvent-based biocompatible adhesive prevents lifting and flagging from the printed base film'
MF_FILM_LINER = 'Sustainable 50 lb. roll-form release liner made from up to 30% post-consumer waste'
MF_OL_LINER = '1 mil ultra smooth clear polyester liner for excellent adhesive wet out yielding optimum clarity'
def medflex(flx, model, face, adh, liner, cert, width, name_cn, overlam=False):
    key = 'mf_' + flx
    feats = (['Cross platform printability','Exceptional fine printability and barcode scanning with super smooth 2 mil polyesters','Smudge proof and abrasion resistant thermal transfer printing with robust gloss and matte topcoats'] if not overlam else
             ['1 mil gloss clear and matte clear polyester overlaminates ensure label legibility remains intact for the lifetime of the medical device'])
    records[key] = {
        'model': model,
        'name_en': model,
        'name_cn': name_cn,
        'facestock_raw': face,
        'adhesive_raw': adh,
        'liner': liner,
        'thickness_raw': '',
        'temp_raw': '',
        'chem_raw': '',
        'sectors': ['MEDICAL'],
        'cert': cert,
        'features': feats + [f'Master width {width}'],
        'benefits': ['FDA requires medical devices to have product markings that remain intact and legible throughout the lifetime of the device; MedFlex® meets labeling demands for Class I and II medical devices used outside of the body','Immediately adoptable into your UL listing','Global availability – United States, Europe, & Asia (Quick-Ship)'],
        'app_desc': 'Medical device labeling & tracking (Class I and II medical devices used outside the body)',
        'source_category_raw': 'Healthcare > Medical Device > Flexcon® MedFlex®',
        'url': MEDFLEX_URL,
        'tds': MEDFLEX_PDF,
        '_flx': 'FLX' + flx, '_part': '',
    }
    order.append(key)

medflex('069870','MedFlex® Plus MMSMGS50K','2 mil silver matte polyester, gloss topcoat',MF_FILM_ADH,MF_FILM_LINER,MF_FILM_CERT,'54"','MedFlex® Plus MMSMGS50K 2密尔哑面银聚酯(PET)医疗器械标签膜,光面涂层')
medflex('069873','MedFlex® Plus MMSMMS50K','2 mil silver matte polyester, matte topcoat',MF_FILM_ADH,MF_FILM_LINER,MF_FILM_CERT,'60"','MedFlex® Plus MMSMMS50K 2密尔哑面银聚酯(PET)医疗器械标签膜,哑面涂层')
medflex('069868','MedFlex® Plus PMCGS50K','2 mil clear polyester, gloss topcoat',MF_FILM_ADH,MF_FILM_LINER,MF_FILM_CERT,'60"','MedFlex® Plus PMCGS50K 2密尔透明聚酯(PET)医疗器械标签膜,光面涂层')
medflex('069871','MedFlex® Plus PMCMMS50K','2 mil clear matte polyester, matte topcoat',MF_FILM_ADH,MF_FILM_LINER,MF_FILM_CERT,'60"','MedFlex® Plus PMCMMS50K 2密尔哑光透明聚酯(PET)医疗器械标签膜,哑面涂层')
medflex('069869','MedFlex® Plus PMWGS50K','2 mil white polyester, gloss topcoat',MF_FILM_ADH,MF_FILM_LINER,MF_FILM_CERT,'60"','MedFlex® Plus PMWGS50K 2密尔白色聚酯(PET)医疗器械标签膜,光面涂层')
medflex('069872','MedFlex® Plus PMWMS50K','2 mil white polyester, matte topcoat',MF_FILM_ADH,MF_FILM_LINER,MF_FILM_CERT,'60','MedFlex® Plus PMWMS50K 2密尔白色聚酯(PET)医疗器械标签膜,哑面涂层')
medflex('056662','MedFlex® Overlam OMMCS100P','1 mil matte clear polyester overlaminate',MF_OL_ADH,MF_OL_LINER,MF_OL_CERT,'60"','MedFlex® Overlam OMMCS100P 1密尔哑光透明聚酯(PET)医疗器械标签覆膜',overlam=True)
medflex('056663','MedFlex® Overlam OMGCS100P','1 mil gloss clear polyester overlaminate',MF_OL_ADH,MF_OL_LINER,MF_OL_CERT,'60"','MedFlex® Overlam OMGCS100P 1密尔光面透明聚酯(PET)医疗器械标签覆膜',overlam=True)

# ---------------- name_cn overrides for entries the auto-translator handled poorly ----------------
NAME_CN = {
 '301': 'PharmCal® CryoFlex™ 000301 光面涂层2.0密尔透明聚丙烯(PP)深冻/冷链标签材料',
 '12547': 'ThermlFilm® PM 200 白色聚酯(PET)标签膜 TC-390面涂层 V-606胶(汽车发动机舱盖标签)',
 '51249': 'ThermlFilm® MM 500 拉丝不锈钢面聚酯(PET)铭牌/装饰标签膜 TC-390面涂层 V-606胶',
 '54149': 'Flexcon® 2178SL 增强尼龙基材双面胶带(SA 3000有机硅胶/V-246胶),单面硅化底纸',
 'auto_070414': 'ThermlFilm™ HT PI2W50GV2 白色聚酰亚胺(PI)耐高温电路板标签膜',
 'fm_054150': 'Flexcon® 2201SL 增强尼龙基材双面胶带(SA 3000有机硅胶/V-246胶),双面硅化底纸',
 'fm_000491': 'FlexMount® TT 400 L-606 转移胶带,60 LA PFW底纸',
}
for k, v in NAME_CN.items():
    if k in records:
        records[k]['name_cn'] = v

# ---------------- final output ----------------
final = []
for k in order:
    r = records[k]
    r = dict(r)
    flx = r.pop('_flx',''); part = r.pop('_part','')
    extra = [x for x in (flx, part) if x]
    if extra:
        r['features'] = r['features'] + [' / '.join(extra)]
    r['sectors'] = r['sectors'] or []
    final.append(r)

json.dump({'records': final}, open(f'{BASE}/records_raw.json','w'), ensure_ascii=False, indent=1)
print('records:', len(final))
from collections import Counter
c = Counter(s for r in final for s in r['sectors'])
print(c)
print('with tds:', sum(1 for r in final if r['tds']))
print('no url:', [r['model'] for r in final if not r['url']][:10])

# ---------------- unverified.json ----------------
unv = {
 'unverified': [
  {'name': 'Flexcon® SA Series Silicone Adhesives (individual part numbers)',
   'reason': 'Spotlight page describes the SA Series family (incl. SA1000 Series) but publishes no individual product numbers or spec tables; recorded as a single family-level record only.',
   'url': SITE + '/spotlights/silicone-adhesives'},
  {'name': 'PharmCal® Supreme per-product service temperature',
   'reason': 'The Pharmaceutical Labeling Solutions PDF shows two temperature columns (-40°F to 212°F and -40°F to 302°F) as checkbox columns whose row alignment could not be reliably read from the PDF layout; temp_raw left blank for the 5 Supreme products rather than guessing.',
   'url': PHARM_PDF},
  {'name': 'Flexcon PharmCal® products available in Europe',
   'reason': 'EU product list PDF (Flexcon Pharmaceutical Products EU.pdf) linked from the PharmCal spotlight was not downloaded/parsed to stay within the request budget; only North America PharmCal products captured.',
   'url': 'https://assets-us-01.kc-usercontent.com/5ebad2e9-8f0a-0050-6e0b-25e9f568a492/08be45ac-5d7b-4e41-aa87-6ad12ce2afb1/Flexcon%20Pharmaceutical%20Products%20EU.pdf'},
  {'name': 'TamperMark™ White Destruct individual products',
   'reason': 'TamperMark spotlight describes a "White Destruct" sub-family; only one destruct construction (FLX027516, TamperMark PE 200 White Destruct) is linked with a product page and captured. Other destruct variants, if any, are not listed on the pages crawled.',
   'url': SITE + '/spotlights/tampermark'},
  {'name': 'FlexMark® L-59FR / FlexMount® L-59FR (068347, 068876, 068348, 068878, 068874) full technical data',
   'reason': 'Product detail pages linked from the L-59FR spotlight return 404; records built from spotlight page text only (no thickness table / service temperature).',
   'url': L59_URL},
  {'name': 'DermaFlex™ P.E.F. 32 WHITE H-778 90 PFW full technical data',
   'reason': 'Product detail page (products/68293) returns 404; record built from DermaFlex spotlight text only.',
   'url': SITE + '/spotlights/dermaflex'},
 ],
 'blocked_urls': [
  SITE + '/products/68293/dermaflex-pef-32-white-h-778-90-pfw-19-21',
  SITE + '/products/68347/flexmark-l-59fr-068347-flexcon-flexmark-pi-200-amber-v-59fr-spec-50k-9',
  SITE + '/products/68348/flexmark-l-59fr-068348-flexcon-flexmark-foil-200-silver-v-59fr-spec-50k-9',
  SITE + '/products/68874/flexmount-l-59fr-068874-flexcon-flexmount-tt-400-v-59fr-84-la-pft',
  SITE + '/products/68876/flexmark-l-59fr-068876-flexcon-flexmark-pi-200-amber-v-59fr-spec-50k-9-39-41',
  SITE + '/products/68878/flexmark-l-59fr-068878-flexcon-flexmark-foil-200-silver-v-59fr-spec-50k-9-39-41',
 ],
}
json.dump(unv, open(f'{BASE}/unverified.json','w'), ensure_ascii=False, indent=1)
print('unverified written')
