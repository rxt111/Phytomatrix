import io
import json
import urllib.parse
import requests
import pandas as pd
import streamlit as st

from sqlalchemy import inspect
from sqlalchemy.orm import joinedload
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

import database as db

st.set_page_config(page_title="PhytoMatrix R&D Engine", page_icon="🌿", layout="wide")

@st.cache_resource
def startup_db():
    db.init_db()

startup_db()

if "formulation_tray" not in st.session_state:
    st.session_state.formulation_tray = []

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
            return {"mw": mw, "logp": logp, "tpsa": float(p.get("TPSA", 0)), "smiles": p.get("CanonicalSMILES", "N/A"), "lipinski": f"Pass ({viol} Violations)" if viol <= 1 else f"Fail ({viol} Violations)"}
    except Exception:
        pass
    return {"mw": 0, "logp": 0, "tpsa": 0, "smiles": "N/A", "lipinski": "Unknown"}

def evaluate_powder_rheology(bulk_d: float, tapped_d: float) -> dict:
    if bulk_d <= 0 or tapped_d <= 0 or tapped_d < bulk_d:
        return {"carr": 0, "hausner": 0, "flow": "Invalid Density Inputs"}
    carr = 100 * (1 - (bulk_d / tapped_d))
    hausner = tapped_d / bulk_d
    flow = "Excellent" if carr <= 10 else "Good" if carr <= 15 else "Fair" if carr <= 20 else "Poor (Needs Glidant)"
    return {"carr": round(carr, 2), "hausner": round(hausner, 2), "flow": flow}

def generate_pdf_dossier(plant_name: str, bom_df: pd.DataFrame, rheo: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = [
        Paragraph(f"<b>Technical Specification Dossier: {plant_name}</b>", styles['Heading1']),
        Spacer(1, 10),
        Paragraph("<b>1. Powder Rheology & Physical Properties</b>", styles['Heading2']),
        Table([["Metric", "Value", "Impact"], ["Carr's Index", f"{rheo['carr']}%", rheo['flow']], ["Hausner Ratio", f"{rheo['hausner']}", "Compression Quality"]], colWidths=[150, 100, 250]),
        Spacer(1, 15),
        Paragraph("<b>2. Master Bill of Materials</b>", styles['Heading2'])
    ]
    bom_rows = [["Ingredient", "Grade", "Mass (mg)", "% w/w"]]
    for _, r in bom_df.iterrows():
        bom_rows.append([str(r["Ingredient"]), str(r["Grade"]), str(r["Mass (mg)"]), str(r["% w/w"])])
    story.append(Table(bom_rows, colWidths=[180, 150, 80, 90]))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def check_db_diagnostics() -> dict:
    session = db.SessionLocal()
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        counts = {}
        if "botanicals" in tables: counts["botanicals"] = session.query(db.Botanical).count()
        if "phytochemicals" in tables: counts["phytochemicals"] = session.query(db.Phytochemical).count()
        if "formulations" in tables: counts["formulations"] = session.query(db.Formulation).count()
        return {"tables": tables, "counts": counts, "status": "Connected & Healthy"}
    finally:
        session.close()

# Sidebar Navigation Setup
with st.sidebar:
    st.title("🌿 PhytoMatrix R&D")
    nav = st.radio("Navigation", ["🔍 Botanical Explorer", "🏭 Manufacturing SOP & Quality", "🗄️ Database Diagnostics"])
    st.divider()
    
    st.subheader("🛒 Polyherbal Tray")
    for idx, item in enumerate(st.session_state.formulation_tray):
        st.caption(f"{idx+1}. {item['latin_name']} ({item['part']}) - {item['standardization']}")
    if st.button("Clear Tray", use_container_width=True):
        st.session_state.formulation_tray = []
        st.rerun()

    st.divider()
    st.subheader("💾 Saved Recipes")
    recipes = db.get_saved_formulations()
    if recipes:
        sel_rec = st.selectbox("Load Recipe", options=[r["id"] for r in recipes], format_func=lambda x: next(r["name"] for r in recipes if r["id"] == x))
        if st.button("Load Recipe", use_container_width=True):
            r_data = next(r for r in recipes if r["id"] == sel_rec)
            st.session_state.formulation_tray = r_data["items"]
            st.rerun()

# Fetch Botanicals safely with Eager Loading (Fixes DetachedInstanceError)
session = db.SessionLocal()
botanicals = session.query(db.Botanical).options(joinedload(db.Botanical.phytochemicals)).all()
session.close()

if nav == "🔍 Botanical Explorer":
    st.title("🔍 Botanical & Phytochemical Explorer")
    if botanicals:
        selected_latin = st.selectbox("Select Botanical Entity:", [b.latin_name for b in botanicals])
        bot_entity = next(b for b in botanicals if b.latin_name == selected_latin)
        
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Common Name:** {bot_entity.common_name}")
            st.write(f"**Taxonomic Family:** {bot_entity.family}")
            st.write(f"**Synonyms:** {', '.join(json.loads(bot_entity.synonyms_json))}")
        
        with c2:
            st.subheader("Add to Polyherbal Tray")
            part = st.selectbox("Plant Part:", ["Root", "Leaf", "Stem", "Rhizome", "Whole Plant"])
            grade = st.selectbox("Extract Standardization:", ["Crude Powder", "5% Extract", "10% Standardized Extract", "50% Highly Purified"])
            mass = st.number_input("Unit Mass (mg):", value=250.0, step=25.0)
            if st.button("Add to Active Tray", type="primary"):
                st.session_state.formulation_tray.append({"latin_name": bot_entity.latin_name, "part": part, "standardization": grade, "unit_mass_mg": mass})
                st.success("Added to tray!")
                st.rerun()

        st.divider()
        st.subheader("🧪 Phytochemical Constituents")
        for p in bot_entity.phytochemicals:
            with st.expander(f"🔬 {p.name} ({p.chemical_class})"):
                st.write(f"**Plant Part:** {p.plant_part} | **Status:** {p.status}")
                pub_data = fetch_pubchem_data(p.name)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Molecular Weight", f"{pub_data['mw']} g/mol")
                m2.metric("LogP", pub_data['logp'])
                m3.metric("TPSA", f"{pub_data['tpsa']} Å²")
                m4.metric("Lipinski Rule", pub_data['lipinski'])

elif nav == "🏭 Manufacturing SOP & Quality":
    st.title("🏭 Manufacturing SOP & Quality IPQC")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Powder Physics Input")
        bulk_d = st.number_input("Bulk Density (g/mL):", value=0.45, step=0.01)
        tapped_d = st.number_input("Tapped Density (g/mL):", value=0.60, step=0.01)
        rheo = evaluate_powder_rheology(bulk_d, tapped_d)
        st.metric("Carr's Index", f"{rheo['carr']}%")
        st.metric("Hausner Ratio", rheo['hausner'])
        st.info(f"**Flowability:** {rheo['flow']}")

    with col2:
        st.subheader("Export Technical Dossier")
        sample_bom = pd.DataFrame([
            {"Ingredient": "Botanical Active", "Grade": "10% Standardized", "Mass (mg)": 250, "% w/w": "50.0%"},
            {"Ingredient": "Microcrystalline Cellulose", "Grade": "Binder (PH-102)", "Mass (mg)": 245, "% w/w": "49.0%"},
            {"Ingredient": "Colloidal Silicon Dioxide", "Grade": "Glidant", "Mass (mg)": 5, "% w/w": "1.0%"}
        ])
        pdf_bytes = generate_pdf_dossier("Polyherbal Active", sample_bom, rheo)
        st.download_button("📥 Download PDF Dossier", data=pdf_bytes, file_name="Technical_Specification.pdf", mime="application/pdf", type="primary")

elif nav == "🗄️ Database Diagnostics":
    st.title("🗄️ Database Diagnostics & Health")
    health = check_db_diagnostics()
    st.json(health)
