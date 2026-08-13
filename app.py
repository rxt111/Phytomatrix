import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# ⚙️ PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="PhytoMatrix Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .main-header { font-size: 2.2rem; font-weight: 700; color: #10B981; }
        .sub-header { font-size: 1rem; color: #9CA3AF; margin-bottom: 1.5rem; }
        .hero-title { font-size: 4rem; font-weight: 800; color: #10B981; text-align: center; margin-bottom: 0px; }
        .hero-subtitle { font-size: 1.25rem; color: #9CA3AF; text-align: center; margin-bottom: 2rem; }
        .badge-pass { background-color: #065F46; color: #34D399; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
        .badge-risk-mod { background-color: #78350F; color: #FBBF24; padding: 3px 10px; border-radius: 4px; font-weight: 600; }
        .card-box { background-color: #1F2937; padding: 1.2rem; border-radius: 8px; border: 1px solid #374151; margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🔄 SESSION STATE MANAGEMENT
# ==========================================
if "searched_plant" not in st.session_state:
    st.session_state.searched_plant = "Withania somnifera (Ashwagandha)"

# ==========================================
# 🗂️ SIDEBAR NAVIGATION (ALWAYS VISIBLE)
# ==========================================
st.sidebar.image("https://img.icons8.com/isometric-folders/100/leaf.png", width=50)
st.sidebar.title("PhytoMatrix")
st.sidebar.caption("Ethnopharmacological Intelligence")

st.sidebar.markdown(f"**Active Botanical:**\n`{st.session_state.searched_plant}`")

st.sidebar.divider()

# Navigation without label title or "Module" word
navigation_choice = st.sidebar.radio(
    "",
    [
        "🏠 Home & Botanical Search",
        "🌿 Botanical Taxonomy & Identification",
        "🧪 Phytochemistry Master Summary",
        "🏛️ Traditional Medicine Systems",
        "⚖️ Patent & FTO Assessment",
        "🧬 Pharmacological Profile & MoA",
        "🕸️ Network Pharmacology",
        "⚠️ Safety, Toxicology & Interactions",
        "🏥 Clinical Evidence & Human Trials",
        "📚 Literature References & Bibliography"
    ],
    label_visibility="collapsed"
)

# ==========================================
# 🏠 HOME & BOTANICAL SEARCH
# ==========================================
if "Home" in navigation_choice:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<div class='hero-title'>PhytoMatrix</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Ethnopharmacological Intelligence Platform</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        with st.form(key="search_form"):
            search_input = st.text_input(
                "",
                placeholder="Search botanical species (e.g. Withania somnifera, Curcuma longa)...",
                label_visibility="collapsed"
            )
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                submit_button = st.form_submit_button("🔍 Search PhytoMatrix", use_container_width=True)
            
            if submit_button and search_input.strip():
                st.session_state.searched_plant = search_input.strip()
                st.success(f"Loaded database for: {st.session_state.searched_plant}")
                st.rerun()

        st.markdown("<br><p style='text-align: center; color: #9CA3AF;'>Featured Botanicals:</p>", unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        if b1.button("🌿 Ashwagandha", use_container_width=True):
            st.session_state.searched_plant = "Withania somnifera (Ashwagandha)"
            st.rerun()
        if b2.button("🟡 Turmeric", use_container_width=True):
            st.session_state.searched_plant = "Curcuma longa (Turmeric)"
            st.rerun()
        if b3.button("🍃 Gotu Kola", use_container_width=True):
            st.session_state.searched_plant = "Centella asiatica (Gotu Kola)"
            st.rerun()

# ==========================================
# 🌿 BOTANICAL TAXONOMY (HERBARIUM VOUCHER REMOVED)
# ==========================================
elif "Taxonomy" in navigation_choice:
    st.header("🌿 Botanical Taxonomy & Identification")
    st.markdown(f"**Species Query:** `{st.session_state.searched_plant}`")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Taxonomic Nomenclature")
        tax_data = {
            "Attribute": ["Scientific Name", "Family", "Genus", "Species", "Author Citation", "Accepted Status"],
            "Detail": [st.session_state.searched_plant, "Solanaceae (Nightshade family)", "Withania", "somnifera", "(L.) Dunal", "Accepted (POWO / IPNI)"]
        }
        st.table(pd.DataFrame(tax_data))
        
        st.subheader("Vernacular & Local Names")
        vernacular_df = pd.DataFrame({
            "Language / Region": ["Sanskrit", "Hindi", "Tamil", "English", "Mandarin (TCM)"],
            "Vernacular Name": ["Ashwagandha, Varada", "Asgandh", "Amukkara", "Indian Ginseng, Winter Cherry", "A Swa Gan Da"]
        })
        st.dataframe(vernacular_df, use_container_width=True)

    with col2:
        st.subheader("Geographic Origin & Habitat")
        st.info("**Native Range:** India, Middle East, Parts of North/East Africa")
        st.success("**Cultivation Regions:** Mediterranean, Subtropical Asia, Australia")

# ==========================================
# 🧪 PHYTOCHEMISTRY (2D STRUCTURE, SYNONYMS & OTHER PLANTS)
# ==========================================
elif "Phytochemistry" in navigation_choice:
    st.header("🧪 Phytochemistry Master Summary")
    st.markdown(f"**Species Query:** `{st.session_state.searched_plant}`")
    st.markdown("---")
    
    compounds_data = [
        {
            "Plant Name": st.session_state.searched_plant,
            "Compound Name": "Withaferin A",
            "PubChem CID": "265237",
            "CAS Number": "5119-65-3",
            "MW (g/mol)": 470.6,
            "Molecular Formula": "C28H38O6",
            "Class of Compound": "Steroidal Lactone (Withanolide)"
        },
        {
            "Plant Name": st.session_state.searched_plant,
            "Compound Name": "Withanolide A",
            "PubChem CID": "11294378",
            "CAS Number": "32911-62-9",
            "MW (g/mol)": 470.6,
            "Molecular Formula": "C28H38O6",
            "Class of Compound": "Steroidal Lactone (Withanolide)"
        },
        {
            "Plant Name": st.session_state.searched_plant,
            "Compound Name": "Sitoindoside IX",
            "PubChem CID": "152980",
            "CAS Number": "139906-81-3",
            "MW (g/mol)": 632.8,
            "Molecular Formula": "C34H48O11",
            "Class of Compound": "Glycowithanolide"
        }
    ]
    
    df_compounds = pd.DataFrame(compounds_data)
    st.dataframe(df_compounds, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🔍 Compound Detailed Inspector")
    
    selected_compound = st.selectbox("Select Compound to Inspect", df_compounds["Compound Name"].tolist())
    
    # Detailed Phytochemistry View
    if selected_compound == "Withaferin A":
        col_img, col_details = st.columns([1, 2])
        
        with col_img:
            st.subheader("2D Structure")
            # Live PubChem 2D Structure Rendering
            st.image(
                "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/265237/PNG?image_size=300x300", 
                caption="Withaferin A - 2D Molecular Structure",
                width=280
            )
            
        with col_details:
            st.subheader("Synonyms & Chemical Identifiers")
            st.write("**IUPAC Name:** (4β,5β,6β,22R)-4,27-dihydroxy-5,6-epoxy-1-oxowitha-2,24-dienolide")
            st.write("**Chemical Synonyms:** 4β,27-Dihydroxy-5β,6β-epoxy-1-oxowitha-2,24-dienolide, NSC 273757, Withaferine A")
            st.write("**SMILES Code:**")
            st.code("CC1=C(C(=O)OC1)C(C)C2CCC3C2(CCC4C3C5C(O4)(C(=O)C=CC5(C)O)C)C", language="text")
            
            st.markdown("---")
            st.subheader("🌿 Occurrence in Other Plant Species")
            st.write("Beyond *Withania somnifera*, this constituent is reported in:")
            other_plants_df = pd.DataFrame({
                "Species Name": ["Withania coagulans", "Physalis alkekengi", "Tubocapsicum anomalum", "Acnistus arborescens"],
                "Family": ["Solanaceae", "Solanaceae", "Solanaceae", "Solanaceae"],
                "Plant Part Isolated": ["Fruits & Roots", "Leaves", "Aerial Parts", "Leaves"],
                "Yield / Concentration": ["0.18% w/w", "0.05% w/w", "0.03% w/w", "0.12% w/w"]
            })
            st.table(other_plants_df)

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
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Energetics (Pancha Padartha)")
            st.write("**Rasa (Taste):** Tikta (Bitter), Kashaya (Astringent), Madhura (Sweet)")
            st.write("**Guna (Qualities):** Laghu (Light), Snigdha (Unctuous)")
            st.write("**Virya (Potency):** Ushna (Heating)")
            st.write("**Vipaka (Post-Digestive):** Madhura (Sweet)")
        with col2:
            dosha_df = pd.DataFrame({"Dosha": ["Vata", "Pitta", "Kapha"], "Effect": [-1, 0, -1]})
            fig = px.line_polar(dosha_df, r='Effect', theta='Dosha', line_close=True)
            st.plotly_chart(fig, use_container_width=True)

    with tab_tcm:
        st.subheader("Traditional Chinese Medicine")
        st.write("**Four Natures:** Warm (Wēn) | **Five Flavors:** Sweet, Bitter")
        st.write("**Meridians:** Kidney, Heart, Spleen")

    with tab_unani:
        st.subheader("Unani Tibb Profile")
        st.write("**Mizaj:** Garam 2° (Hot), Khushk 2° (Dry) | **Action:** Muqawwi-e-Asab")

    with tab_siddha:
        st.subheader("Siddha Profile")
        st.write("**Mukkuttram:** Pacifies Vatham & Kapham | **Action:** Kaya Kalpam")

    with tab_kampo:
        st.subheader("Kampo System")
        st.write("**Sho Pattern:** Kyo-sho (Deficiency Pattern)")

    with tab_western:
        st.subheader("Western Herbalism")
        st.write("**Action:** Adaptogen, Modulates HPA-Axis")

# ==========================================
# ⚖️ PATENT & FTO ASSESSMENT (CLICK FOR SUMMARY)
# ==========================================
elif "Patent" in navigation_choice:
    st.header("⚖️ Patent Summary & Freedom to Operate (FTO)")
    st.markdown("---")
    
    patents_data = [
        {
            "Patent ID": "US10894068B2",
            "Title": "Standardized Extract Formulations for Cognitive Support",
            "Assignee": "Natreon Inc.",
            "Filing Date": "2017-03-15",
            "Expiry Date": "2037-03-15",
            "Status": "Active 🟢",
            "Abstract": "A high-purity aqueous extract of Withania somnifera comprising at least 8% withanolide glycosides and low withaferin A (<0.5%) for enhancing memory and reducing serum cortisol.",
            "Key Claims": "Claim 1: Composition comprising 8-15% withanolide glycosides and <0.2% free withaferin A.\nClaim 4: Method of treating stress-induced fatigue via oral administration.",
            "FTO Impact": "Restricts commercializing standardized aqueous extracts matching this exact ratio until 2037."
        },
        {
            "Patent ID": "EP2892543B1",
            "Title": "High-Yield Extraction Method for Active Biomarkers",
            "Assignee": "Sabinsa Corp",
            "Filing Date": "2013-08-10",
            "Expiry Date": "2033-08-10",
            "Status": "Active 🟢",
            "Abstract": "Process for selective extraction of steroidal lactones using supercritical CO2 with ethanol co-solvent at 40-60°C and 250 bar pressure.",
            "Key Claims": "Claim 1: A green extraction method utilizing scCO2 with 5% v/v ethanol co-solvent.\nClaim 7: Yield exceeding 92% active bio-compounds.",
            "FTO Impact": "Process patent only. Does not block traditional ethanol/water extraction."
        }
    ]
    
    df_patents = pd.DataFrame(patents_data)
    st.dataframe(df_patents[["Patent ID", "Title", "Assignee", "Filing Date", "Expiry Date", "Status"]], use_container_width=True)
    
    st.markdown("---")
    st.subheader("📑 Interactive Patent Summary & FTO Inspector")
    
    selected_patent_id = st.selectbox("Select Patent ID to View Detailed Summary", df_patents["Patent ID"].tolist())
    
    p_info = next(item for item in patents_data if item["Patent ID"] == selected_patent_id)
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown(f"### {p_info['Patent ID']} - {p_info['Title']}")
        st.write(f"**Assignee:** {p_info['Assignee']}")
        st.write(f"**Expiry Date:** {p_info['Expiry Date']}")
        st.markdown("**Abstract:**")
        st.info(p_info["Abstract"])
        
    with col_p2:
        st.markdown("**Key Independent Claims:**")
        st.code(p_info["Key Claims"], language="text")
        st.markdown("**Freedom To Operate (FTO) Assessment:**")
        st.warning(p_info["FTO Impact"])

# ==========================================
# 🧬 PHARMACOLOGY
# ==========================================
elif "Pharmacological" in navigation_choice:
    st.header("🧬 Pharmacological Profile & Mechanisms (MoA)")
    st.markdown("---")
    
    targets_data = [
        {"Target Gene / Protein": "GABA-A Receptor", "UniProt ID": "P18507", "Action": "Agonist / Modulator", "Compound": "Withanolide A", "Potency": "EC50 = 12.4 µM"},
        {"Target Gene / Protein": "COX-2 (PTGS2)", "UniProt ID": "P35354", "Action": "Inhibitor", "Compound": "Withaferin A", "Potency": "IC50 = 8.5 µM"},
        {"Target Gene / Protein": "NF-κB (RELA)", "UniProt ID": "Q04206", "Action": "Translocation Inhibitor", "Compound": "Withaferin A", "Potency": "IC50 = 1.2 µM"}
    ]
    st.dataframe(pd.DataFrame(targets_data), use_container_width=True)

# ==========================================
# 🕸️ NETWORK PHARMACOLOGY (NEW SECTION)
# ==========================================
elif "Network Pharmacology" in navigation_choice:
    st.header("🕸️ Network Pharmacology Analysis")
    st.markdown(f"**Target-Disease-Compound Interactions for:** `{st.session_state.searched_plant}`")
    st.markdown("---")
    
    col_net1, col_net2 = st.columns([2, 1])
    
    with col_net1:
        st.subheader("Compound-Target Network Visualizer")
        
        # Plotly Network Interaction Map
        fig_net = go.Figure()
        
        # Node Coordinates
        nodes_x = [0, 0, 1, 1, 1, 2, 2]
        nodes_y = [2, 0, 3, 1, -1, 2, 0]
        node_text = ["Withaferin A", "Withanolide A", "GABA-A", "NF-kB", "COX-2", "Anxiety", "Inflammation"]
        node_type = ["Compound", "Compound", "Target", "Target", "Target", "Disease", "Disease"]
        node_color = ["#10B981", "#10B981", "#3B82F6", "#3B82F6", "#3B82F6", "#EF4444", "#EF4444"]
        
        # Edges
        edges = [(0, 3), (0, 4), (1, 2), (3, 6), (4, 6), (2, 5)]
        
        for edge in edges:
            fig_net.add_trace(go.Scatter(
                x=[nodes_x[edge[0]], nodes_x[edge[1]]],
                y=[nodes_y[edge[0]], nodes_y[edge[1]]],
                mode='lines',
                line=dict(color='#4B5563', width=2),
                hoverinfo='none'
            ))
            
        fig_net.add_trace(go.Scatter(
            x=nodes_x, y=nodes_y,
            mode='markers+text',
            text=node_text,
            textposition="top center",
            marker=dict(size=24, color=node_color, line=dict(color='white', width=2)),
            hoverinfo='text'
        ))
        
        fig_net.update_layout(
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=400,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_net, use_container_width=True)

    with col_net2:
        st.subheader("Degree Centrality (Hub Targets)")
        hub_data = pd.DataFrame({
            "Target Symbol": ["RELA (NF-kB)", "PTGS2 (COX-2)", "GABRA1", "TNF", "AKT1"],
            "Degree": [18, 14, 12, 9, 7],
            "Betweenness": [0.42, 0.31, 0.28, 0.15, 0.11]
        })
        st.dataframe(hub_data, use_container_width=True)
        
    st.markdown("---")
    st.subheader("KEGG Pathway Enrichment Map")
    kegg_df = pd.DataFrame({
        "Pathway Name": ["Neuroactive ligand-receptor interaction", "NF-kappa B signaling pathway", "IL-17 signaling pathway", "Pathways in cancer"],
        "Gene Count": [14, 11, 8, 15],
        "p-Value": [1.2e-7, 3.4e-6, 1.1e-4, 4.2e-4]
    })
    fig_bar = px.bar(kegg_df, x='Gene Count', y='Pathway Name', orientation='h', color='p-Value', color_continuous_scale='Viridis')
    st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# ⚠️ SAFETY & TOXICOLOGY
# ==========================================
elif "Safety" in navigation_choice:
    st.header("⚠️ Safety, Toxicology & Herb-Drug Interactions")
    st.markdown("---")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.subheader("Toxicological Benchmarks")
        st.write("• **Acute Oral LD50:** > 2000 mg/kg")
        st.write("• **Sub-Chronic NOAEL:** 500 mg/kg/day")
    with col_s2:
        st.subheader("CYP Inhibition Profile")
        st.table(pd.DataFrame({
            "Enzyme": ["CYP3A4", "CYP2D6"],
            "Effect": ["Moderate Inhibition", "Mild Induction"]
        }))

# ==========================================
# 🏥 CLINICAL EVIDENCE
# ==========================================
elif "Clinical" in navigation_choice:
    st.header("🏥 Clinical Evidence & Human Trials")
    st.markdown("---")
    st.dataframe(pd.DataFrame([
        {"Indication": "Stress & Cortisol Reduction", "Studies": 12, "Sample Size": "N = 840", "Grade": "🟢 Grade A"},
        {"Indication": "Sleep Quality & Insomnia", "Studies": 8, "Sample Size": "N = 520", "Grade": "🟢 Grade A"}
    ]), use_container_width=True)

# ==========================================
# 📚 LITERATURE REFERENCES
# ==========================================
elif "Literature" in navigation_choice:
    st.header("📚 Literature References & Bibliography")
    st.markdown("---")
    st.dataframe(pd.DataFrame([
        {"Citation ID": "REF-001", "Title": "An Overview on Ashwagandha", "Journal": "Afr J Tradit Complement Altern Med", "Year": 2011},
        {"Citation ID": "REF-002", "Title": "Withaferin A Inhibits NF-kB", "Journal": "J Biol Chem", "Year": 2007}
    ]), use_container_width=True)
