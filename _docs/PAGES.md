# ETIA Website — Page & Image Manifest

**Image naming on COS (clean public URLs, no spaces/Chinese):**
`/img/home/hero-1.jpg` · `/img/brands/<brand>.png` · `/img/industry/<slug>.jpg` · `/img/company/factory-1.jpg` · `/img/product/<model-slug>.jpg`

IMG legend: **★ needed now** · ○ optional/later · — none

| ID | Page | Path (file = path + index.html) | Template | Images |
|----|------|------|------|------|
| H-00 | Home | `/` | home | ★ hero mosaic ×5–6 + brand logos ×5 |
| C-01 | Company | `/company/` | company | ★ factory/converting ×3–5 |
| C-02 | Contact | `/contact/` | contact | ○ office photos |
| C-03 | Service & Support | `/support/` | support | — |
| C-04 | Applications (hub) | `/applications/` | hub | ○ application scene ×3 |
| C-05 | Insights (hub) | `/insights/` | hub | — |
| P-00 | Products & Solutions | `/products/` | landing | ○ 1 banner |
| PI-0 | By Industry (index) | `/products/by-industry/` | index | ○ thumb per industry |
| PS-0 | By Solution (index) | `/products/by-solution/` | index | ○ thumb per solution |
| PM-0 | By Material (index) | `/products/by-material/` | index | ○ thumb per material |

### Industry landing pages (L1 ×8) — ★ one header photo each (you have these)
| ID | Industry | Path | Image file |
|----|------|------|------|
| IND-01 | Electronics Manufacturing & PCB Process | `/products/by-industry/electronics-manufacturing-and-pcb-process/` | `/img/industry/electronics-manufacturing-and-pcb-process.jpg` ★ |
| IND-02 | Automotive & Tire Industry | `/products/by-industry/automotive-and-tire-industry/` | `/img/industry/automotive-and-tire-industry.jpg` ★ |
| IND-03 | Steel & Metal Industry | `/products/by-industry/steel-and-metal-industry/` | `/img/industry/steel-and-metal-industry.jpg` ★ |
| IND-04 | Medical Devices & IVD | `/products/by-industry/medical-devices-and-ivd/` | `/img/industry/medical-devices-and-ivd.jpg` ★ |
| IND-05 | Pharma R&D & Production | `/products/by-industry/pharma-randd-and-production/` | `/img/industry/pharma-randd-and-production.jpg` ★ |
| IND-06 | Outdoor Facilities & Photovoltaics | `/products/by-industry/outdoor-facilities-and-photovoltaics/` | `/img/industry/outdoor-facilities-and-photovoltaics.jpg` ★ |
| IND-07 | Telecom Cabling & Equipment Rooms | `/products/by-industry/telecom-cabling-and-equipment-rooms/` | `/img/industry/telecom-cabling-and-equipment-rooms.jpg` ★ |
| IND-08 | Ceramics & Kilns | `/products/by-industry/ceramics-and-kilns/` | `/img/industry/ceramics-and-kilns.jpg` ★ |

### Solution landing pages (L1 ×8) — ○ optional header
- SOL-01  `/products/by-solution/smt-reflow-and-pcb-process-solutions/`  (SMT Reflow & PCB Process Solutions)
- SOL-02  `/products/by-solution/automotive-end-to-end-identification-solutions/`  (Automotive End-to-End Identification Solutions)
- SOL-03  `/products/by-solution/steel-high-temp-heat-treatment-solutions/`  (Steel High-Temp Heat-Treatment Solutions)
- SOL-04  `/products/by-solution/medical-and-pharmaceutical-compliance-solutions/`  (Medical & Pharmaceutical Compliance Solutions)
- SOL-05  `/products/by-solution/outdoor-pv-and-weatherproof-marking-solutions/`  (Outdoor PV & Weatherproof Marking Solutions)
- SOL-06  `/products/by-solution/telecom-room-and-data-center-solutions/`  (Telecom Room & Data Center Solutions)
- SOL-07  `/products/by-solution/ceramic-kiln-ultra-high-temp-solutions/`  (Ceramic Kiln Ultra-High-Temp Solutions)
- SOL-08  `/products/by-solution/esd-anti-static-and-compliance-solutions/`  (ESD Anti-Static & Compliance Solutions)

### Material landing pages (L1 ×6) — ○ optional header
- MAT-01  `/products/by-material/polyimide-pi/`  (Polyimide (PI))
- MAT-02  `/products/by-material/polyester-pet/`  (Polyester (PET))
- MAT-03  `/products/by-material/ceramic-and-metal-high-temp/`  (Ceramic & Metal High-Temp)
- MAT-04  `/products/by-material/low-temp-weatherable-specialty/`  (Low-Temp Weatherable Specialty)
- MAT-05  `/products/by-material/flame-retardant-and-esd-functional/`  (Flame-Retardant & ESD Functional)
- MAT-06  `/products/by-material/synthetic-paper-and-specialty/`  (Synthetic Paper & Specialty)

### Collection pages (L2) — template, ○ images optional
- Industry sub-process: **33** · Solution sub-scenario: **32** · Material property: **17**  → total **82** collection pages

### Product Detail Pages (PDP) — **131** pages, template `/products/item/<model-slug>/`
- ○ one product photo each → `/img/product/<model-slug>.jpg` (batch later; template works without)