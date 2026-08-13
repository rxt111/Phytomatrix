import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# ⚙️ PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="PhytoMatrix Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished UI
st.markdown("""
    <style>
        .main-header { font-size: 2.2rem; font-weight: 700; color: #10B981; }
        .sub-header { font-size: 1rem; color: #9CA3AF; margin-bottom: 1.5rem; }
        .badge-pass { background-color: #065F46; color: #34D399; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
        .badge-risk-low { background-color: #065F46; color: #34D399; padding: 3px 10px; border-radius: 4px; font-weight: 600; }
        .badge-risk-mod { background-color: #78350F; color: #FBBF24; padding: 3px 10px; border-radius: 4px; font-weight: 600; }
        .badge-risk-high { background-color: #7F1D1D; color: #FCA5A5; padding: 3px 10px; border-radius: 4px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🗂️ SIDEBAR NAVIGATION
# ==========================================
st.sidebar.image("https://img.icons8.com/isometric-folders/100/leaf.png", width=60)
st.sidebar.title("PhytoMatrix")
st.sidebar.caption("Ethnopharmacological Intelligence Platform")

selected_botanical = st.sidebar.selectbox(
    "Select Botanical Species",
    ["Withania somnifera (Ashwagandha)", "Curcuma longa (Turmeric)", "Centella asiatica (Gotu Kola)"]
)

st.sidebar.divider()

# Navigation selection without label title
navigation_choice = st.sidebar.radio(
    "",
    [
        "🌿 Botanical Taxonomy & Identification",
        "🧪 Phytochemistry Master Summary",
        "🏛️ Traditional Medicine Systems",
        "⚖️ Patent & FTO Assessment",
        "🧬 Pharmacological Profile & MoA",
        "⚠️ Safety, Toxicology & Interactions",
        "🏥 Clinical Evidence & Human Trials",
        "📚 Literature References & Bibliography"
    ],
    label_visibility="collapsed"
)

# Top Bar Header
st.markdown("<div class='main-header'>🔬 PhytoMatrix Platform</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-header'>Active Species: <b>{selected_botanical}</b></div>", unsafe_allow_html=True)

# ==========================================
# 🌿 BOTANICAL TAXONOMY
# ==========================================
if "Taxonomy" in navigation_choice:
    st.header("🌿 Botanical Taxonomy & Identification")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Taxonomic Nomenclature")
        tax_data = {
            "Attribute": ["Scientific Name", "Family", "Genus", "Species", "Author Citation", "Accepted Status"],
            "Detail": ["Withania somnifera", "Solanaceae (Nightshade family)", "Withania", "somnifera", "(L.) Dunal", "Accepted (POWO / IPNI)"]
        }
        st.table(pd.DataFrame(tax_data))
        
        st.subheader("Vernacular & Local Names")
        vernacular_df = pd.DataFrame({
            "Language / Region": ["Sanskrit", "Hindi", "Tamil", "English", "Mandarin (TCM)"],
            "Vernacular Name": ["Ashwagandha, Varada", "Asgandh", "Amukkara", "Indian Ginseng, Winter Cherry", "A Swa Gan Da"]
        })
        st.dataframe(vernacular_df, use_container_width=True)

    with col2:
        st.subheader("Geographic Origin")
        st.info("**Native Range:** India, Middle East, Parts of North/East Africa")
        st.success("**Cultivation Regions:** Mediterranean, Subtropical Asia, Australia")
        
        st.subheader("Herbarium Voucher Reference")
        st.json({
            "Repository": "Royal Botanic Gardens, Kew (K)",
            "BarCode": "K000978123",
            "Collector": "L. Dunal",
            "Verification": "POWO Taxonomy ID: 818558-1"
        })

# ==========================================
# 🧪 PHYTOCHEMISTRY
# ==========================================
elif "Phytochemistry" in navigation_choice:
    st.header("🧪 Phytochemistry Master Summary")
    st.markdown("---")
    
    compounds_data = [
        {
            "Plant Name": "Withania somnifera",
            "Compound Name": "Withaferin A",
            "CAS Number": "5119-65-3",
            "MW (g/mol)": 470.6,
            "Molecular Formula": "C28H38O6",
            "Plant Part": "Root, Leaf",
            "Class of Compound": "Steroidal Lactone (Withanolide)"
        },
        {
            "Plant Name": "Withania somnifera",
            "Compound Name": "Withanolide A",
            "CAS Number": "32911-62-9",
            "MW (g/mol)": 470.6,
            "Molecular Formula": "C28H38O6",
            "Plant Part": "Root",
            "Class of Compound": "Steroidal Lactone (Withanolide)"
        },
        {
            "Plant Name": "Withania somnifera",
            "Compound Name": "Sitoindoside IX",
            "CAS Number": "139906-81-3",
            "MW (g/mol)": 632.8,
            "Molecular Formula": "C34H48O11",
            "Plant Part": "Root",
            "Class of Compound": "Glycowithanolide"
        },
        {
            "Plant Name": "Withania somnifera",
            "Compound Name": "Anaferine",
            "CAS Number": "38462-04-3",
            "MW (g/mol)": 224.3,
            "Molecular Formula": "C13H24N2O",
            "Plant Part": "Root",
            "Class of Compound": "Alkaloid"
        }
    ]
    
    df_compounds = pd.DataFrame(compounds_data)
    
    # 7-Column Master Table
    st.dataframe(df_compounds, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🔍 Tier 2: Compound Detailed Profile & Lipinski Evaluation")
    
    selected_compound = st.selectbox("Select Compound to Inspect", df_compounds["Compound Name"].tolist())
    
    if selected_compound == "Withaferin A":
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Identity & Chemistry**")
            st.write("**IUPAC Name:** (4β,5β,6β,22R)-4,27-dihydroxy-5,6-epoxy-1-oxowitha-2,24-dienolide")
            st.write("**PubChem CID:** 265237")
            st.code("CC1=C(C(=O)OC1)C(C)C2CCC3C2(CCC4C3C5C(O4)(C(=O)C=CC5(C)O)C)C", language="text")
        
        with col_b:
            st.markdown("**Lipinski Rule of 5 Evaluation**")
            st.write("• **MW:** 470.6 g/mol (≤ 500) ✅")
            st.write("• **LogP:** 3.2 (≤ 5) ✅")
            st.write("• **HBD:** 2 (≤ 5) ✅")
            st.write("• **HBA:** 6 (≤ 10) ✅")
            st.markdown("<span class='badge-pass'>🟢 Lipinski Status: PASS (0 Violations)</span>", unsafe_allow_html=True)

# ==========================================
# 🏛️ TRADITIONAL MEDICINE SYSTEMS
# ==========================================
elif "Traditional" in navigation_choice:
    st.header("🏛️ Traditional Medicine Systems (6 Frameworks)")
    st.markdown("---")
    
    tab_ayurveda, tab_tcm, tab_unani, tab_siddha, tab_kampo, tab_western = st.tabs([
        "🧘 Ayurveda", "☯️ TCM", "🏺 Unani Tibb", "🛕 Siddha", "🇯🇵 Kampo", "🌿 Western"
    ])
    
    with tab_ayurveda:
        col_ayur1, col_ayur2 = st.columns([2, 1])
        with col_ayur1:
            st.subheader("Energetics (Pancha Padartha)")
            st.write("**Rasa (Taste):** Tikta (Bitter), Kashaya (Astringent), Madhura (Sweet)")
            st.write("**Guna (Qualities):** Laghu (Light), Snigdha (Unctuous)")
            st.write("**Virya (Potency):** Ushna (Heating)")
            st.write("**Vipaka (Post-Digestive):** Madhura (Sweet)")
            
            st.subheader("Primary Actions & Classical Diseases")
            st.write("• **Rasayana (Rejuvenative)** → *Jara* (Aging) & *Kshaya* (Debility)")
            st.write("• **Balya (Strength Promoter)** → *Dhatukshaya* (Tissue Depletion)")
            st.write("• **Nidrajanana (Sleep Inducer)** → *Anidra* (Insomnia)")
        
        with col_ayur2:
            st.subheader("Dosha Impact")
            dosha_df = pd.DataFrame({
                "Dosha": ["Vata", "Pitta", "Kapha"],
                "Effect": [-1, 0, -1]
            })
            fig = px.line_polar(dosha_df, r='Effect', theta='Dosha', line_close=True)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Status: Vata-Kapha Shamaka (Pacifies Vata & Kapha)")

    with tab_tcm:
        st.subheader("Traditional Chinese Medicine (Ben Cao Classification)")
        st.write("**Four Natures (Sì Qì):** Warm (Wēn)")
        st.write("**Five Flavors (Wǔ Wèi):** Sweet, Bitter")
        st.write("**Meridians (Guī Jīng):** Kidney, Heart, Spleen")
        st.write("**Primary Action:** Tonifies Primordial Qi, Calms the Shen (Spirit) → *Shī Mián* (Insomnia)")

    with tab_unani:
        st.subheader("Unani Tibb Framework")
        st.write("**Mizaj (Temperament):** Garam 2° (Hot), Khushk 2° (Dry)")
        st.write("**Primary Actions:** Muqawwi-e-Asab (Nervine Tonic) → *Malikholia* (Melancholia)")

    with tab_siddha:
        st.subheader("Siddha Medicine Profile")
        st.write("**Mukkuttram:** Pacifies Vatham & Kapham")
        st.write("**Primary Action:** Kaya Kalpam (Cellular Rejuvenation) → *Kshayam* (Loss of Vitality)")

    with tab_kampo:
        st.subheader("Japanese Kampo System")
        st.write("**Sho Pattern:** Kyo-sho (Deficiency Pattern)")
        st.write("**Primary Action:** Ki-Tonifying → *Ki-Kyo* (Qi Deficiency / Burnout)")

    with tab_western:
        st.subheader("Western Herbalism Profile")
        st.write("**Energetics:** Warming, Moistening")
        st.write("**Herbal Action:** Adaptogen, Modulates HPA-Axis → Chronic Stress Fatigue")

# ==========================================
# ⚖️ PATENT & FTO
# ==========================================
elif "Patent" in navigation_choice:
    st.header("⚖️ Patent Summary & Freedom to Operate (FTO)")
    st.markdown("---")
    
    st.markdown("### 🛡️ FTO Risk Summary")
    st.markdown("<span class='badge-risk-mod'>MODERATE FTO RISK LEVEL</span>", unsafe_allow_html=True)
    st.info("Traditional water/ethanol decoctions are in the public domain (protected via TKDL prior art). However, high-potency standardized extract ratios and liposomal delivery systems carry active utility patents.")
    
    st.subheader("Master Global Patent Summary Table")
    patents = [
        {
            "Patent ID": "US10894068B2",
            "Title": "Standardized Extract Formulations for Cognitive Support",
            "Assignee": "Natreon Inc.",
            "Filing Date": "2017-03-15",
            "Expiry Date": "2037-03-15",
            "Jurisdiction": "USPTO (USA)",
            "Legal Status": "Active 🟢",
            "Category": "Composition & Use"
        },
        {
            "Patent ID": "EP2892543B1",
            "Title": "High-Yield Extraction Method for Active Biomarkers",
            "Assignee": "Sabinsa Corp",
            "Filing Date": "2013-08-10",
            "Expiry Date": "2033-08-10",
            "Jurisdiction": "EPO (Europe)",
            "Legal Status": "Active 🟢",
            "Category": "Process Patent"
        }
    ]
    st.dataframe(pd.DataFrame(patents), use_container_width=True)

# ==========================================
# 🧬 PHARMACOLOGY
# ==========================================
elif "Pharmacological" in navigation_choice:
    st.header("🧬 Pharmacological Profile & Mechanisms (MoA)")
    st.markdown("---")
    
    st.subheader("Molecular Targets & Binding Affinities")
    targets_data = [
        {"Target Gene / Protein": "GABA-A Receptor", "UniProt ID": "P18507", "Action": "Agonist / Modulator", "Compound": "Withanolide A", "Potency Metric": "EC50 = 12.4 µM"},
        {"Target Gene / Protein": "COX-2 (PTGS2)", "UniProt ID": "P35354", "Action": "Inhibitor", "Compound": "Withaferin A", "Potency Metric": "IC50 = 8.5 µM"},
        {"Target Gene / Protein": "NF-κB (RELA)", "UniProt ID": "Q04206", "Action": "Translocation Inhibitor", "Compound": "Withaferin A", "Potency Metric": "IC50 = 1.2 µM"}
    ]
    st.dataframe(pd.DataFrame(targets_data), use_container_width=True)
    
    st.subheader("KEGG Pathway Involvement")
    st.write("• **NF-κB Signaling Pathway** (Downregulation of TNF-α, IL-6)")
    st.write("• **Nrf2-ARE Antioxidant Pathway** (Upregulation of SOD, Catalase)")

# ==========================================
# ⚠️ SAFETY & TOXICOLOGY
# ==========================================
elif "Safety" in navigation_choice:
    st.header("⚠️ Safety, Toxicology & Herb-Drug Interactions")
    st.markdown("---")
    
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        st.subheader("Toxicological Benchmarks")
        st.write("• **Acute Oral Toxicity (LD50):** > 2000 mg/kg (Practically Non-Toxic)")
        st.write("• **Sub-Chronic NOAEL (Rat 90-day):** 500 mg/kg/day")
        st.write("• **Genotoxicity (Ames Test):** Negative (Non-mutagenic)")
        st.warning("⚠️ **NIH LiverTox Status:** Low risk of HILI. Rare mild liver transaminase elevation reported at extreme doses (>1500 mg/day).")

    with col_s2:
        st.subheader("Cytochrome P450 (CYP) Profile")
        cyp_df = pd.DataFrame({
            "Enzyme System": ["CYP3A4", "CYP2D6", "P-Glycoprotein (P-gp)"],
            "Effect": ["Moderate Inhibition", "Mild Induction", "Weak Substrate"],
            "Clinical Severity": ["🟡 Moderate", "🟢 Low", "🟡 Moderate"]
        })
        st.table(cyp_df)

# ==========================================
# 🏥 CLINICAL EVIDENCE
# ==========================================
elif "Clinical" in navigation_choice:
    st.header("🏥 Clinical Evidence & Human Trials")
    st.markdown("---")
    
    st.subheader("Tier 1: Clinical Evidence Summary by Indication")
    evidence_summary = [
        {"Indication": "Stress & Cortisol Reduction", "Total Studies": 12, "Sample Size": "N = 840", "Grade": "🟢 Grade A (High)", "Key Outcome": "27.9% reduction in serum cortisol"},
        {"Indication": "Sleep Quality & Insomnia", "Total Studies": 8, "Sample Size": "N = 520", "Grade": "🟢 Grade A (High)", "Key Outcome": "Significant reduction in sleep onset latency"}
    ]
    st.dataframe(pd.DataFrame(evidence_summary), use_container_width=True)

# ==========================================
# 📚 LITERATURE REFERENCES
# ==========================================
elif "Literature" in navigation_choice:
    st.header("📚 Literature References & Bibliography")
    st.markdown("---")
    
    st.subheader("Searchable Citation Database")
    citations = [
        {
            "Citation ID": "REF-001",
            "Title": "An Overview on Ashwagandha: A Rasayana of Ayurveda",
            "Journal": "Afr J Tradit Complement Altern Med",
            "Year": 2011,
            "DOI": "10.4314/ajtcam.v8i5S.9",
            "Study Type": "Review Article"
        },
        {
            "Citation ID": "REF-002",
            "Title": "Withaferin A Inhibits NF-κB Activation via Inhibition of IκB Kinase",
            "Journal": "J Biol Chem",
            "Year": 2007,
            "DOI": "10.1074/jbc.M610330200",
            "Study Type": "In Vitro Bioassay"
        }
    ]
    
    df_refs = pd.DataFrame(citations)
    st.dataframe(df_refs, use_container_width=True)
    
    st.subheader("Format Citation Exporter")
    ref_sel = st.selectbox("Select Paper", df_refs["Title"].tolist())
    st.code(f"{ref_sel}. Afr J Tradit Complement Altern Med. 2011;8(5S):9-13. doi:10.4314/ajtcam.v8i5S.9", language="text")
