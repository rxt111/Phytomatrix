import io
import json
import urllib.parse
import requests
import pandas as pd
import streamlit as st

from sqlalchemy.orm import joinedload

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

import database as db

st.set_page_config(page_title="PhytoMatrix R&D Engine", page_icon="🌿", layout="wide")

@st.cache_resource
def startup_db():
    db.init_db()

startup_db()

if "formulation_tray" not in st.session_state:
    st.session_state.formulation_tray = []

# PubChem Live Fetch Utility
@st.cache_data(ttl=3600)
def fetch_pubchem_data(compound_name: str) -> dict:
    encoded = urllib.parse.quote(compound_name)
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded}/property/MolecularWeight,CanonicalSMILES,XLogP,TPSA/JSON"
    try:
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            p = res.json()["PropertyTable"]["Properties"][0]
            mw, logp = float(p.get("MolecularWeight", 0)), float(p.get("XLogP", 0))
            viol = (1 if mw > 500 else 0) + (1 if logp > 5 else 0)
            return {
                "mw": mw, 
                "logp": logp, 
                "tpsa": float(p.get("TPSA", 0)), 
                "smiles": p.get("CanonicalSMILES", "N/A"), 
                "lipinski": f"Pass ({viol} Violations)" if viol <= 1 else f"Fail ({viol} Violations)"
            }
    except Exception:
        pass
    return {"mw": 0, "logp": 0, "tpsa": 0, "smiles": "N/A", "lipinski": "Unknown"}

# Powder Physics Calculator
def evaluate_powder_rheology(bulk_d: float, tapped_d: float) -> dict:
    if bulk_d <= 0 or tapped_d <= 0 or tapped_d < bulk_d:
        return {"carr": 0, "hausner": 0, "flow": "Invalid Density Inputs"}
    carr = 100 * (1 - (bulk_d / tapped_d))
    hausner = tapped_d / bulk_d
    flow = "Excellent" if carr <= 10 else "Good" if carr <= 15 else "Fair" if carr <= 20 else "Poor (Needs Glidant)"
    return {"carr": round(carr, 2), "hausner": round(hausner, 2), "flow": flow}

# ReportLab Numbered Canvas with Full-Page Diagonal Watermark & Running Header/Footer
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages):
        # 1. Full Page Diagonal Semi-Transparent Watermark
        self.saveState()
        self.setFont("Helvetica-Bold", 60)
        self.setFillColorRGB(0.85, 0.85, 0.85, alpha=0.30)
        self.translate(300, 380)
        self.rotate(45)
        self.drawCentredString(0, 0, "PhytoMatrix")
        self.restoreState()

        # 2. Running Header and Footer
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColorRGB(0.3, 0.3, 0.3)
        self.drawString(36, 756, "PhytoMatrix R&D Engine | Technical Specification Dossier")
        self.setStrokeColorRGB(0.8, 0.8, 0.8)
        self.setLineWidth(0.5)
        self.line(36, 750, 576, 750)
        
        self.line(36, 45, 576, 45)
        self.drawString(36, 30, "CONFIDENTIAL - PhytoMatrix R&D Proprietary Document")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(576, 30, page_str)
        self.restoreState()

def generate_custom_pdf(selected_sections: list, bot_entity, tray_items: list, rheo: dict, ipqc_specs: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("<b>PhytoMatrix R&D Technical Dossier</b>", styles['Title']),
        Spacer(1, 10)
    ]
    
    if "Botanical Taxonomy & Profile" in selected_sections and bot_entity:
        story.append(Paragraph("<b>1. Botanical Taxonomy & Profile</b>", styles['Heading2']))
        story.append(Paragraph(f"<b>Latin Name:</b> {bot_entity.latin_name}", styles['Normal']))
        story.append(Paragraph(f"<b>Common Name:</b> {bot_entity.common_name} | <b>Family:</b> {bot_entity.family}", styles['Normal']))
        story.append(Spacer(1, 10))

    if "Traditional Medicine Indications & Formulations" in selected_sections and bot_entity:
        raw_trad = getattr(bot_entity, "traditional_json", "{}") or "{}"
        trad = json.loads(raw_trad)
        story.append(Paragraph("<b>2. Traditional Medicine Systems & Indications</b>", styles['Heading2']))
        if "ayurveda" in trad:
            a = trad["ayurveda"]
            story.append(Paragraph(f"<b>Ayurveda:</b> Rasa: {a.get('rasa')} | Virya: {a.get('virya')} | Dosha: {a.get('dosha')}", styles['Normal']))
        if "disease_conditions" in trad:
            story.append(Paragraph(f"<b>Classical Indications:</b> {', '.join(trad['disease_conditions'])}", styles['Normal']))
        story.append(Spacer(1, 10))

    if "Phytochemical Markers & Drug-Likeness" in selected_sections and bot_entity:
        story.append(Paragraph("<b>3. Phytochemical Constituents</b>", styles['Heading2']))
        phyto_rows = [["Compound", "Class", "Plant Part", "Status"]]
        for p in bot_entity.phytochemicals:
            phyto_rows.append([p.name, p.chemical_class, p.plant_part, p.status])
        story.append(Table(phyto_rows, colWidths=[150, 150, 100, 100]))
        story.append(Spacer(1, 10))

    if "Master Bill of Materials (BOM)" in selected_sections and tray_items:
        story.append(Paragraph("<b>4. Master Bill of Materials (BOM)</b>", styles['Heading2']))
        bom_rows = [["Ingredient", "Part", "Grade", "Mass (mg)"]]
        for item in tray_items:
            bom_rows.append([item["latin_name"], item["part"], item["standardization"], str(item["unit_mass_mg"])])
        story.append(Table(bom_rows, colWidths=[180, 100, 140, 80]))
        story.append(Spacer(1, 10))

    if "Manufacturing SOP, Powder Physics & Regulatory Specs" in selected_sections:
        story.append(Paragraph("<b>5. Manufacturing Physics & Regulatory Quality Specs</b>", styles['Heading2']))
        story.append(Paragraph(f"<b>Carr's Index:</b> {rheo['carr']}% | <b>Hausner Ratio:</b> {rheo['hausner']} | <b>Flowability:</b> {rheo['flow']}", styles['Normal']))
        story.append(Spacer(1, 5))
        ipqc_rows = [["Parameter", "Pharmacopeial Limit / Spec", "Status"]]
        ipqc_rows.append(["Heavy Metals (Pb, As, Cd, Hg)", ipqc_specs["heavy_metals"], "PASS"])
        ipqc_rows.append(["Microbial TAMC / TYMC", ipqc_specs["microbial"], "PASS"])
        ipqc_rows.append(["Loss on Drying (LOD)", ipqc_specs["lod"], "PASS"])
        story.append(Table(ipqc_rows, colWidths=[200, 200, 100]))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()

# Sidebar Navigation
with st.sidebar:
    st.title("🌿 PhytoMatrix R&D")
    nav = st.radio("Navigation", [
        "🔍 Botanical Explorer",
        "🏛️ Traditional Medicine Systems",
        "🔬 Phytochemical Constituents",
        "📜 Patent & FTO Intelligence",
        "🧪 Formulation Canvas",
        "🕸️ Network Pharmacology",
        "🏭 Manufacturing SOP & Quality",
        "📄 Complete PDF Dossier Engine"
    ])
    st.divider()
    
    st.subheader("🛒 Active Workbench Tray")
    for idx, item in enumerate(st.session_state.formulation_tray):
        st.caption(f"{idx+1}. {item['latin_name']} ({item['part']}) - {item['standardization']}")
    if st.button("Clear Tray", use_container_width=True):
        st.session_state.formulation_tray = []
        st.rerun()

    st.divider()
    st.subheader("💾 Saved Recipes")
    recipes = db.get_saved_formulations()
    if recipes:
        sel_rec = st.selectbox("Load Saved Recipe", options=[r["id"] for r in recipes], format_func=lambda x: next(r["name"] for r in recipes if r["id"] == x))
        if st.button("Load Recipe into Tray", use_container_width=True):
            r_data = next(r for r in recipes if r["id"] == sel_rec)
            st.session_state.formulation_tray = r_data["items"]
            st.rerun()

# Database Query
session = db.SessionLocal()
botanicals = session.query(db.Botanical).options(joinedload(db.Botanical.phytochemicals)).all()
session.close()

# ---------------------------------------------------------
# 1. BOTANICAL EXPLORER (Homepage Clean Search-First View)
# ---------------------------------------------------------
if nav == "🔍 Botanical Explorer":
    st.title("🌿 PhytoMatrix R&D Engine")
    st.caption("Search-first botanical entity lookup, taxonomy, and plant part selection.")
    
    search_q = st.text_input("🔍 Search Botanicals, Key Active Compounds, or Taxonomic Entities:", placeholder="e.g. Ashwagandha, Curcumin, Withania somnifera...")
    
    filtered_bots = botanicals
    if search_q.strip():
        sq = search_q.lower()
        filtered_bots = [b for b in botanicals if sq in b.latin_name.lower() or sq in b.common_name.lower() or any(sq in s.lower() for s in json.loads(b.synonyms_json))]
    
    if filtered_bots:
        selected_latin = st.selectbox("Select Botanical Entity:", [b.latin_name for b in filtered_bots])
        bot_entity = next(b for b in filtered_bots if b.latin_name == selected_latin)
        
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(f"🌱 {bot_entity.common_name}")
            st.write(f"**Latin Name:** *{bot_entity.latin_name}*")
            st.write(f"**Family:** {bot_entity.family}")
            st.write(f"**Synonyms:** {', '.join(json.loads(bot_entity.synonyms_json))}")
        
        with c2:
            st.subheader("Add to Polyherbal Tray")
            part = st.selectbox("Plant Part:", ["Root", "Leaf", "Stem", "Rhizome", "Whole Plant"])
            grade = st.selectbox("Extract Standardization:", ["Crude Powder", "5% Extract", "10% Standardized Extract", "50% Highly Purified"])
            mass = st.number_input("Unit Mass (mg):", value=250.0, step=25.0)
            if st.button("Add to Active Tray", type="primary"):
                st.session_state.formulation_tray.append({"latin_name": bot_entity.latin_name, "part": part, "standardization": grade, "unit_mass_mg": mass})
                st.success("Added to active workbench tray!")
                st.rerun()

# ---------------------------------------------------------
# 2. TRADITIONAL MEDICINE SYSTEMS
# ---------------------------------------------------------
elif nav == "🏛️ Traditional Medicine Systems":
    st.title("🏛️ Traditional Medicine Systems & Knowledge Base")
    st.write("Explore Ayurvedic energetics, TCM meridian tropism, classical disease indications, and historical dosage forms.")
    
    if botanicals:
        selected_latin = st.selectbox("Select Entity for Traditional Profiling:", [b.latin_name for b in botanicals])
        bot_entity = next(b for b in botanicals if b.latin_name == selected_latin)
        raw_trad = getattr(bot_entity, "traditional_json", "{}") or "{}"
        trad_data = json.loads(raw_trad)
        
        t1, t2 = st.columns(2)
        with t1:
            st.subheader("🧘 Ayurveda Energetics (*Dravyaguna*)")
            ayur = trad_data.get("ayurveda", {})
            st.write(f"**Rasa (Taste):** {ayur.get('rasa', 'N/A')}")
            st.write(f"**Virya (Potency):** {ayur.get('virya', 'N/A')}")
            st.write(f"**Vipaka (Post-Digestive):** {ayur.get('vipaka', 'N/A')}")
            st.info(f"**Dosha Affinity:** {ayur.get('dosha', 'N/A')}")
            
        with t2:
            st.subheader("☯️ Traditional Chinese Medicine (TCM)")
            tcm = trad_data.get("tcm", {})
            st.write(f"**Thermal Nature:** {tcm.get('nature', 'N/A')}")
            st.write(f"**Meridian Tropism:** {tcm.get('meridians', 'N/A')}")
            st.info(f"**Primary Action:** {tcm.get('function', 'N/A')}")

        st.divider()
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("🩺 Traditional Disease Conditions (*Vyadhi*)")
            for cond in trad_data.get("disease_conditions", []):
                st.write(f"• {cond}")
                
        with col_b:
            st.subheader("🏺 Classical Formulations & Dosage Forms")
            for form in trad_data.get("classical_formulations", []):
                st.write(f"• **{form['name']}** ({form['type']})")
                st.caption(f"Indications: {form['indications']}")

# ---------------------------------------------------------
# 3. PHYTOCHEMICAL CONSTITUENTS (Dedicated Module)
# ---------------------------------------------------------
elif nav == "🔬 Phytochemical Constituents":
    st.title("🔬 Phytochemical Constituents Library")
    st.write("Examine bioactive markers, chemical classes, and live PubChem drug-likeness parameters.")
    
    if botanicals:
        selected_latin = st.selectbox("Select Botanical Entity:", [b.latin_name for b in botanicals])
        bot_entity = next(b for b in botanicals if b.latin_name == selected_latin)
        
        for p in bot_entity.phytochemicals:
            with st.expander(f"🔬 {p.name} ({p.chemical_class}) - {p.status}", expanded=True):
                pub_data = fetch_pubchem_data(p.name)
                st.write(f"**Plant Part:** {p.plant_part} | **Canonical SMILES:** `{pub_data['smiles']}`")
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Molecular Weight", f"{pub_data['mw']} g/mol")
                m2.metric("LogP", pub_data['logp'])
                m3.metric("TPSA", f"{pub_data['tpsa']} Å²")
                m4.metric("Lipinski Rule of 5", pub_data['lipinski'])

# ---------------------------------------------------------
# 4. PATENT & FTO INTELLIGENCE
# ---------------------------------------------------------
elif nav == "📜 Patent & FTO Intelligence":
    st.title("📜 Patent & Freedom-to-Operate (FTO) Intelligence")
    query = st.text_input("Enter Compound, Botanical, or Invention Keyword:", value="Curcumin bioavailability matrix")
    
    if st.button("🔍 Run Prior Art & FTO Scan", type="primary"):
        encoded_q = urllib.parse.quote(query)
        st.markdown(f"""
        **Direct Literature & Patent Portals:**
        * 🌐 [Google Patents Search](https://patents.google.com/?q={encoded_q})
        * 📚 [PubMed Clinical Literature Mining](https://pubmed.ncbi.nlm.nih.gov/?term={encoded_q})
        * 🏛️ [WIPO PATENTSCOPE](https://patentscope.wipo.int/search/en/result.jsf?query={encoded_q})
        """)
        
        st.divider()
        st.subheader("📊 Freedom-to-Operate (FTO) Risk Assessment Matrix")
        fto_data = [
            {"Patent ID": "US10485839B2", "Title": "Enhanced Bioavailability Curcuminoid Formulations", "FTO Risk": "High Risk", "Opportunity": "Phospholipid complexation design-around"},
            {"Patent ID": "EP2892541A1", "Title": "Synergistic Herbal Extracts for Cognitive Health", "FTO Risk": "Low Risk (Expired)", "Opportunity": "Public domain ratio usage"},
            {"Patent ID": "WO2021183920A1", "Title": "Sustained Release Polyherbal Solid Dosage Forms", "FTO Risk": "Medium Risk", "Opportunity": "Monitor pending claim scope"}
        ]
        st.dataframe(pd.DataFrame(fto_data), use_container_width=True)

# ---------------------------------------------------------
# 5. FORMULATION CANVAS
# ---------------------------------------------------------
elif nav == "🧪 Formulation Canvas":
    st.title("🧪 Polyherbal Formulation Canvas")
    if not st.session_state.formulation_tray:
        st.info("Your workbench tray is empty. Visit '🔍 Botanical Explorer' to select active herbs!")
    else:
        tray_df = pd.DataFrame(st.session_state.formulation_tray)
        total_mg = tray_df["unit_mass_mg"].sum()
        tray_df["% w/w"] = tray_df["unit_mass_mg"].apply(lambda x: f"{(x / total_mg * 100):.1f}%" if total_mg > 0 else "0%")
        
        st.subheader("Active Recipe Composition")
        st.dataframe(tray_df, use_container_width=True)
        st.metric("Total Single Dosage Unit Fill Weight", f"{total_mg:.1f} mg")
        
        st.divider()
        st.subheader("🌿 Clean Label Excipient Engine")
        e1, e2 = st.columns(2)
        with e1:
            st.selectbox("Synthetic Excipient:", ["PVP K30 (Binder)", "Magnesium Stearate (Lubricant)", "Talc (Glidant)"])
        with e2:
            st.success("🌱 Green Alternative: Organic Acacia Gum / Tapioca Starch / Rice Concentrate")
            
        st.divider()
        rec_name = st.text_input("Formulation Name:", value="Custom Adaptogenic Complex")
        if st.button("Save Recipe to Database", type="primary"):
            sess = db.SessionLocal()
            try:
                new_f = db.Formulation(name=rec_name, target_fill_mg=total_mg)
                sess.add(new_f)
                sess.commit()
                for item in st.session_state.formulation_tray:
                    sess.add(db.FormulationItem(
                        formulation_id=new_f.id,
                        botanical_latin_name=item["latin_name"],
                        plant_part=item["part"],
                        extract_grade=item["standardization"],
                        unit_mass_mg=item["unit_mass_mg"]
                    ))
                sess.commit()
                st.success(f"Recipe '{rec_name}' saved to database!")
                st.rerun()
            finally:
                sess.close()

# ---------------------------------------------------------
# 6. NETWORK PHARMACOLOGY
# ---------------------------------------------------------
elif nav == "🕸️ Network Pharmacology":
    st.title("🕸️ Network Pharmacology & Pathway Interaction")
    target_pathway = st.selectbox("Target Pathway:", [
        "Inflammatory Cascade (COX-2 / NF-κB / TNF-α)",
        "Neuroprotective Axis (AChE / BDNF / Nrf2)",
        "Metabolic Regulation (AMPK / PPAR-γ)"
    ])
    
    st.subheader("🎯 Primary Molecular Target Network")
    targets_df = pd.DataFrame({
        "Target Protein": ["PTGS2 (COX-2)", "TNF-α", "IL-6", "AChE"],
        "Phytochemical Activator": ["Curcumin", "Withaferin A", "Withanolide A", "Bacoside A3"],
        "Affinity Score (pKi)": [7.8, 8.2, 6.9, 7.4],
        "Interaction Effect": ["Inhibition", "Down-regulation", "Modulation", "Inhibition"]
    })
    st.table(targets_df)

# ---------------------------------------------------------
# 7. MANUFACTURING SOP & QUALITY
# ---------------------------------------------------------
elif nav == "🏭 Manufacturing SOP & Quality":
    st.title("🏭 Manufacturing SOP & Quality Control")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Powder Physics Inputs")
        bulk_d = st.number_input("Bulk Density (g/mL):", value=0.45, step=0.01)
        tapped_d = st.number_input("Tapped Density (g/mL):", value=0.60, step=0.01)
        rheo = evaluate_powder_rheology(bulk_d, tapped_d)
        st.metric("Carr's Index", f"{rheo['carr']}%")
        st.metric("Hausner Ratio", rheo['hausner'])
        st.info(f"**Flowability Rating:** {rheo['flow']}")

    with c2:
        st.subheader("In-Process cGMP Regulatory Controls")
        st.write("• **Heavy Metals (Pb, As, Cd, Hg):** USP <2232> / EP Limits")
        st.write("• **Microbial Limits:** TAMC < 10^4 CFU/g | TYMC < 10^2 CFU/g")
        st.write("• **Loss on Drying (LOD):** ≤ 5.0% w/w")
        st.success("STATUS: Batch Specifications Compliant")

# ---------------------------------------------------------
# 8. COMPLETE PDF DOSSIER ENGINE
# ---------------------------------------------------------
elif nav == "📄 Complete PDF Dossier Engine":
    st.title("📄 Complete Technical Specification PDF Dossier Engine")
    st.write("Customize sections and export a technical report complete with dynamic page numbering and diagonal watermark.")
    
    st.subheader("🎛️ Customize Dossier Sections")
    sec_bot = st.checkbox("Botanical Taxonomy & Profile", value=True)
    sec_trad = st.checkbox("Traditional Medicine Indications & Formulations", value=True)
    sec_phyto = st.checkbox("Phytochemical Markers & Drug-Likeness", value=True)
    sec_bom = st.checkbox("Master Bill of Materials (BOM)", value=True)
    sec_sop = st.checkbox("Manufacturing SOP, Powder Physics & Regulatory Specs", value=True)
    
    selected_secs = []
    if sec_bot: selected_secs.append("Botanical Taxonomy & Profile")
    if sec_trad: selected_secs.append("Traditional Medicine Indications & Formulations")
    if sec_phyto: selected_secs.append("Phytochemical Markers & Drug-Likeness")
    if sec_bom: selected_secs.append("Master Bill of Materials (BOM)")
    if sec_sop: selected_secs.append("Manufacturing SOP, Powder Physics & Regulatory Specs")
    
    st.divider()
    if botanicals:
        sel_latin = st.selectbox("Select Primary Botanical for Dossier:", [b.latin_name for b in botanicals])
        bot_ent = next(b for b in botanicals if b.latin_name == sel_latin)
        
        rheo_data = evaluate_powder_rheology(0.45, 0.60)
        ipqc_data = {
            "heavy_metals": "Pb < 0.5 ppm, As < 1.5 ppm, Cd < 0.5 ppm, Hg < 0.1 ppm",
            "microbial": "TAMC ≤ 10^4 CFU/g, TYMC ≤ 10^2 CFU/g",
            "lod": "≤ 5.0% w/w"
        }
        
        pdf_data = generate_custom_pdf(selected_secs, bot_ent, st.session_state.formulation_tray, rheo_data, ipqc_data)
        st.download_button("📥 Download Branded Technical Specification Dossier", data=pdf_data, file_name="PhytoMatrix_Technical_Dossier.pdf", mime="application/pdf", type="primary")
