import os
import sys
import json
import uuid
import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="PRISM | Multi-Channel Content Synthesis",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for polished Hackathon UI
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    .badge-pass {
        background-color: #059669;
        color: white;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-fail {
        background-color: #dc2626;
        color: white;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .provenance-card {
        background: rgba(99, 102, 241, 0.08);
        border-left: 4px solid #6366f1;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .source-span-box {
        background: rgba(0, 0, 0, 0.25);
        border: 1px dashed rgba(255, 255, 255, 0.2);
        border-radius: 6px;
        padding: 8px 12px;
        font-family: monospace;
        font-size: 0.85rem;
        color: #cbd5e1;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Imports from prism package
from prism.state import PRISMState
from prism.config import (
    DEFAULT_GROQ_API_KEY,
    DEFAULT_MODEL,
    OUTPUTS_DIR,
    DB_PATH
)
from prism.persistence.db import save_run, get_run, list_runs, delete_run, init_db
from prism.graph import prism_app

# Ensure directories & DB exist
init_db()
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Initialize Session State
if "current_run" not in st.session_state:
    st.session_state.current_run = None
if "run_history" not in st.session_state:
    st.session_state.run_history = []

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/prism.png", width=60)
    st.title("🔮 PRISM Controls")
    st.caption("Provenance-Reasoned Intelligent Synthesis for Multi-channel Content")
    st.markdown("---")

    # API Configuration
    st.subheader("⚙️ LLM Settings")
    groq_api_key = st.text_input(
        "Groq API Key",
        value=os.environ.get("GROQ_API_KEY", DEFAULT_GROQ_API_KEY),
        type="password",
        help="Groq Cloud API Key"
    )
    if groq_api_key:
        os.environ["GROQ_API_KEY"] = groq_api_key

    groq_model = st.selectbox(
        "Model",
        options=["openai/gpt-oss-20b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "llama3-70b-8192"],
        index=0
    )
    os.environ["PRISM_GROQ_MODEL"] = groq_model

    st.markdown("---")

    # Content Parameters
    st.subheader("🎯 Content Configuration")
    selected_tone = st.selectbox(
        "Tone",
        options=["Professional & Authoritative", "Executive & Visionary", "Technical & Analytical", "Conversational & Engaging", "Direct & Persuasive"],
        index=0
    )
    selected_audience = st.selectbox(
        "Target Audience",
        options=["Enterprise Executives", "Technical Engineers", "General Public", "Investors & Board", "Cross-functional Teams"],
        index=0
    )
    selected_objective = st.text_input(
        "Strategic Objective",
        value="Synthesize core insights with zero hallucination and complete provenance."
    )

    st.markdown("---")
    st.subheader("📡 Multi-Channel Fan-Out")
    st.caption("Select channels to generate:")

    c_li = st.checkbox("LinkedIn Post", value=True)
    c_tw = st.checkbox("Twitter / X Thread", value=True)
    c_sum = st.checkbox("Executive Summary (DOCX)", value=True)
    c_adv = st.checkbox("Strategic Advisory (DOCX)", value=True)
    c_ppt = st.checkbox("Slide Deck Presentation (PPTX)", value=True)

    selected_channels = []
    if c_li: selected_channels.append("linkedin")
    if c_tw: selected_channels.append("twitter")
    if c_sum: selected_channels.append("summary")
    if c_adv: selected_channels.append("advisory")
    if c_ppt: selected_channels.append("presentation")

    st.markdown("---")
    st.caption(f"💾 Database: `{os.path.basename(DB_PATH)}`")

# Header Section
st.markdown('<div class="main-title">PRISM Content Synthesis Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title"><b>One Source → One Fact Graph → Multi-Channel Outputs → Guardrail Consistency Critic → Bounded Revision → Verifiable Provenance</b></div>', unsafe_allow_html=True)

# Main Workspace Tabs
main_tab1, main_tab2, main_tab3, main_tab4, main_tab5, main_tab6 = st.tabs([
    "🚀 Input & Synthesize",
    "🧠 Fact Graph (Truth)",
    "📑 Multi-Channel Outputs",
    "🛡️ Guardrail Critic & Revision",
    "🔗 Provenance Inspector",
    "🗄️ Run History & Database"
])

# ==============================================================================
# TAB 1: INPUT & GENERATE
# ==============================================================================
with main_tab1:
    col_in1, col_in2 = st.columns([3, 2])

    with col_in1:
        st.subheader("1. Source Document Input")
        input_mode = st.radio("Input Method", ["Paste Raw Text", "Upload Document (PDF / DOCX / TXT)"], horizontal=True)

        input_text = ""
        uploaded_file_path = None

        if input_mode == "Paste Raw Text":
            preset = st.selectbox(
                "Or load a sample document:",
                [
                    "Custom Input",
                    "PRISM System Architecture",
                    "Quarterly AI Financial Brief",
                    "Medical Research Executive Summary"
                ]
            )

            if preset == "PRISM System Architecture":
                sample_default = """PRISM is an AI-powered content generation system.
It takes a source document and creates multiple content formats.
PRISM uses a centralized Fact Graph to maintain consistency across generated outputs.
The Fact Graph extracts entities, claims with source spans, metrics, dates, and recommendations as the single source of truth.
The platform includes an automated Guardrail Consistency Critic that flags unsupported claims and triggers bounded revisions.
Recent benchmarks show PRISM reduces cross-channel authoring time by 75% while achieving 100% factual provenance verification."""
            elif preset == "Quarterly AI Financial Brief":
                sample_default = """Nexus Global reported Q3 2026 revenue of $4.8 billion, representing a 28% year-over-year growth driven by enterprise AI adoption.
Operating margins expanded to 34.2%, up 450 basis points from Q3 2025.
The company announced an expanded capital expenditure of $1.2 billion for next-generation GPU compute clusters.
CEO Marcus Vance confirmed that cloud net retention reached 132%, with over 4,200 enterprise customers actively deploying generative agents.
Key risks highlighted include semiconductor supply constraints and regulatory compliance across EU jurisdictions."""
            elif preset == "Medical Research Executive Summary":
                sample_default = """The Phase III trial of CardiaGuard demonstrated a 42% relative reduction in major cardiovascular events among 6,400 enrolled patients over a 24-month period.
Primary endpoints were met with statistical significance (p < 0.001).
Adverse event rates were comparable to placebo at 3.1% versus 2.9%.
The clinical advisory board recommends priority FDA filing by Q1 2027.
The study was conducted across 48 clinical research sites in North America and Western Europe."""
            else:
                sample_default = ""

            input_text = st.text_area(
                "Source Text",
                value=sample_default,
                height=220,
                placeholder="Enter or paste your source document text here..."
            )
            input_type = "text"

        else:
            uploaded_file = st.file_uploader("Upload PDF, DOCX, or TXT file", type=["pdf", "docx", "txt"])
            if uploaded_file is not None:
                save_dir = os.path.join(OUTPUTS_DIR, "uploads")
                os.makedirs(save_dir, exist_ok=True)
                file_dest = os.path.join(save_dir, uploaded_file.name)
                with open(file_dest, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                uploaded_file_path = file_dest
                st.success(f"Uploaded: {uploaded_file.name}")
                input_type = "file"
            else:
                input_type = "file"

    with col_in2:
        st.subheader("2. Generation Summary")
        st.markdown(f"""
        <div class="metric-card">
            <b>Selected Channels:</b> {len(selected_channels)} ({', '.join(selected_channels) if selected_channels else 'None'})<br>
            <b>Tone:</b> {selected_tone}<br>
            <b>Target Audience:</b> {selected_audience}<br>
            <b>Model:</b> <code>{groq_model}</code><br>
            <b>RAG Engine:</b> FAISS + all-MiniLM-L6-v2<br>
            <b>Single Source of Truth:</b> Fact Graph (Structured)<br>
            <b>Guardrail Critic:</b> Active with Bounded Revision
        </div>
        """, unsafe_allow_html=True)

        if not selected_channels:
            st.warning("⚠️ Please select at least one output channel from the sidebar.")

        generate_btn = st.button("🚀 Run PRISM Synthesis Pipeline", type="primary", use_container_width=True, disabled=len(selected_channels) == 0)

    if generate_btn:
        if input_type == "text" and not input_text.strip():
            st.error("Please provide source text before starting generation.")
        elif input_type == "file" and not uploaded_file_path:
            st.error("Please upload a supported file before starting generation.")
        else:
            run_id = f"run_{str(uuid.uuid4())[:8]}"
            initial_state: PRISMState = {
                "input_type": input_type,
                "file_path": uploaded_file_path,
                "input_text": input_text if input_type == "text" else None,
                "source_text": "",
                "normalized_text": "",
                "fact_graph": {},
                "tone": selected_tone,
                "audience": selected_audience,
                "objective": selected_objective,
                "selected_outputs": selected_channels,
                "linkedin_output": None,
                "twitter_output": None,
                "summary_output": None,
                "advisory_output": None,
                "presentation_output": None,
                "pptx_path": None,
                "guardrail_result": None,
                "failed_output": None,
                "revision_count": 0,
                "provenance": [],
                "rag_chunks": [],
                "rag_vector_store": None,
                "rag_retriever": None,
                "run_id": run_id,
                "rendered_assets": {}
            }

            with st.status("🔮 Executing PRISM Pipeline...", expanded=True) as status_box:
                st.write("📥 Step 1: Ingesting & normalizing source text...")
                st.write("🧠 Step 2: Extracting Fact Graph (Entities, Claims, Metrics, Dates, Risks)...")
                st.write("🔍 Step 3: Indexing RAG chunks with FAISS vector store...")
                st.write(f"📡 Step 4: Fan-out generation to {len(selected_channels)} specialist agents...")
                st.write("🛡️ Step 5: Guardrail Consistency Critic verifying factual grounding...")
                st.write("🔗 Step 6: Generating claim-to-source-span provenance mappings...")
                st.write("📄 Step 7: Multi-format rendering (PPTX / DOCX / MD / TXT)...")
                st.write("💾 Step 8: Persisting run and outputs to SQLite database...")

                try:
                    final_state = prism_app.invoke(initial_state)
                    st.session_state.current_run = final_state
                    status_box.update(label="✅ PRISM Synthesis Complete!", state="complete", expanded=False)
                    st.success(f"🎉 Run `{run_id}` completed and saved successfully!")
                except Exception as e:
                    status_box.update(label="❌ Pipeline Failed", state="error")
                    st.error(f"Error during execution: {str(e)}")

# Active run data helper
curr = st.session_state.current_run

# ==============================================================================
# TAB 2: FACT GRAPH (Truth)
# ==============================================================================
with main_tab2:
    if not curr or not curr.get("fact_graph"):
        st.info("💡 Run the pipeline or select a past run from the History tab to inspect the Fact Graph.")
    else:
        fg = curr.get("fact_graph", {})
        st.subheader("🧠 Fact Graph — Single Source of Truth")
        st.markdown(f"**Synopsis:** {fg.get('synopsis', 'N/A')}")

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Entities", len(fg.get("entities", [])))
        m_col2.metric("Factual Claims", len(fg.get("claims", [])))
        m_col3.metric("Metrics", len(fg.get("metrics", [])))
        m_col4.metric("Recommendations", len(fg.get("recommendations", [])))

        st.markdown("---")

        # Claims breakdown with source spans and confidence
        st.markdown("### 📋 Extracted Claims & Ground Truth Source Spans")
        claims = fg.get("claims", [])
        if claims:
            for i, c in enumerate(claims, 1):
                conf = c.get("confidence", 0.95)
                conf_pct = int(conf * 100) if conf <= 1.0 else int(conf)
                with st.expander(f"Claim {i}: {c.get('text')}", expanded=(i <= 3)):
                    st.markdown(f"**Confidence:** `{conf_pct}%`")
                    st.markdown(f"**Source Passage:**")
                    st.markdown(f'<div class="source-span-box">"{c.get("source_span")}"</div>', unsafe_allow_html=True)
        else:
            st.write("No claims explicitly extracted.")

        # Metrics & Entities
        c_ent, c_met = st.columns(2)
        with c_ent:
            st.markdown("### 🏷️ Entities")
            entities = fg.get("entities", [])
            if entities:
                for e in entities:
                    st.markdown(f"- **{e.get('name')}** (`{e.get('type')}`)")
            else:
                st.write("No entities extracted.")

        with c_met:
            st.markdown("### 📊 Metrics & Numerical Values")
            metrics = fg.get("metrics", [])
            if metrics:
                for m in metrics:
                    st.markdown(f"- **{m.get('name')}:** `{m.get('value')}` (*{m.get('context')}*)")
                    st.caption(f"Source: \"{m.get('source_span')}\"")
            else:
                st.write("No metrics extracted.")

        # Dates & Risks
        c_dat, c_risk = st.columns(2)
        with c_dat:
            st.markdown("### 📅 Dates & Events")
            dates = fg.get("dates", [])
            if dates:
                for d in dates:
                    st.markdown(f"- **{d.get('date')}:** {d.get('event')}")
            else:
                st.write("No dates extracted.")

        with c_risk:
            st.markdown("### ⚠️ Risks & Recommendations")
            risks = fg.get("risks", [])
            if risks:
                st.markdown("**Risks Identified:**")
                for r in risks:
                    st.markdown(f"- ⚠️ {r}")
            recs = fg.get("recommendations", [])
            if recs:
                st.markdown("**Recommendations:**")
                for rec in recs:
                    st.markdown(f"- 💡 {rec.get('text')}")

# ==============================================================================
# TAB 3: MULTI-CHANNEL OUTPUTS
# ==============================================================================
with main_tab3:
    if not curr:
        st.info("💡 Run the pipeline to view generated multi-channel content.")
    else:
        st.subheader("📑 Synthesized Multi-Channel Content")
        selected = curr.get("selected_outputs", [])

        out_tabs = st.tabs([ch.capitalize() for ch in selected] if selected else ["Outputs"])

        for i, ch in enumerate(selected):
            with out_tabs[i]:
                if ch == "linkedin":
                    st.markdown("#### 💼 LinkedIn Post")
                    li_text = curr.get("linkedin_output", "")
                    st.text_area("Generated Post", value=li_text, height=260)
                    st.download_button("📥 Download LinkedIn Markdown", data=li_text, file_name=f"linkedin_{curr.get('run_id')}.md")

                elif ch == "twitter":
                    st.markdown("#### 🐦 Twitter / X Thread / Post")
                    tw_text = curr.get("twitter_output", "")
                    st.text_area("Generated Tweets", value=tw_text, height=260)
                    st.download_button("📥 Download Twitter Text", data=tw_text, file_name=f"twitter_{curr.get('run_id')}.txt")

                elif ch == "summary":
                    st.markdown("#### 📄 Executive Summary")
                    sum_text = curr.get("summary_output", "")
                    st.markdown(sum_text)
                    st.download_button("📥 Download Summary Markdown", data=sum_text, file_name=f"executive_summary_{curr.get('run_id')}.md")

                elif ch == "advisory":
                    st.markdown("#### 🛡️ Strategic Advisory Brief")
                    adv_text = curr.get("advisory_output", "")
                    st.markdown(adv_text)
                    st.download_button("📥 Download Advisory Markdown", data=adv_text, file_name=f"advisory_{curr.get('run_id')}.md")

                elif ch == "presentation":
                    st.markdown("#### 📽️ Slide Deck Presentation")
                    pres = curr.get("presentation_output", {})
                    if pres:
                        st.markdown(f"### {pres.get('title', 'Presentation')}")
                        slides = pres.get("slides", [])
                        for s in slides:
                            with st.expander(f"Slide {s.get('slide_number')}: {s.get('title')}", expanded=True):
                                for bullet in s.get("content", []):
                                    st.markdown(f"- {bullet}")
                    pptx_file = curr.get("pptx_path")
                    if pptx_file and os.path.exists(pptx_file):
                        with open(pptx_file, "rb") as f:
                            st.download_button("📥 Download Presentation PPTX", data=f.read(), file_name=os.path.basename(pptx_file), mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")

# ==============================================================================
# TAB 4: GUARDRAIL CRITIC & REVISION
# ==============================================================================
with main_tab4:
    if not curr or not curr.get("guardrail_result"):
        st.info("💡 Run the pipeline to inspect the Guardrail Consistency Critic.")
    else:
        st.subheader("🛡️ Guardrail Consistency Critic & Revision Audit")
        gr = curr.get("guardrail_result", {})
        overall = gr.get("overall_status", "PASS")
        rev_count = curr.get("revision_count", 0)

        c_g1, c_g2, c_g3 = st.columns(3)
        with c_g1:
            if overall == "PASS":
                st.markdown('Overall Status: <span class="badge-pass">PASS</span>', unsafe_allow_html=True)
            else:
                st.markdown('Overall Status: <span class="badge-fail">FAIL</span>', unsafe_allow_html=True)
        with c_g2:
            st.metric("Total Revision Iterations", rev_count)
        with c_g3:
            st.metric("Outputs Verified", len(gr.get("outputs", {})))

        st.markdown("---")
        st.markdown("### 🔍 Channel-by-Channel Consistency Audit")

        for channel, check in gr.get("outputs", {}).items():
            status = check.get("status", "PASS")
            issues = check.get("issues", [])
            with st.expander(f"Channel: {channel.upper()} — Status: {status}", expanded=(status != "PASS")):
                if status == "PASS":
                    st.success("✅ Output is fully grounded in the Fact Graph with zero unsupported claims.")
                else:
                    st.error(f"❌ Consistency issues detected:")
                    for iss in issues:
                        st.markdown(f"- ⚠️ {iss}")
                    st.info(f"Targeted revision agent invoked to repair {channel} output.")

# ==============================================================================
# TAB 5: PROVENANCE INSPECTOR
# ==============================================================================
with main_tab5:
    if not curr or not curr.get("provenance"):
        st.info("💡 Run the pipeline to explore verifiable claim-to-source provenance links.")
    else:
        st.subheader("🔗 Verifiable Provenance & Grounding Matrix")
        st.caption("Every generated sentence is mapped directly back to its supporting Fact Graph claim and original source passage.")

        prov_list = curr.get("provenance", [])
        st.markdown(f"**Total Provenance Links Generated:** `{len(prov_list)}`")

        # Filter by channel
        channels_in_prov = list(set(p.get("output_channel") for p in prov_list))
        filter_ch = st.selectbox("Filter by Channel:", ["All Channels"] + channels_in_prov)

        for p in prov_list:
            if filter_ch != "All Channels" and p.get("output_channel") != filter_ch:
                continue

            conf = p.get("confidence", 0.95)
            conf_pct = int(conf * 100) if conf <= 1.0 else int(conf)

            st.markdown(f"""
            <div class="provenance-card">
                <b>[{p.get('output_channel', '').upper()}] Output Statement:</b><br>
                "{p.get('output_statement')}"<br><br>
                <b>📌 Grounding Claim:</b> {p.get('claim_text')} &nbsp; <code>Confidence: {conf_pct}%</code>
                <div class="source-span-box">
                    <b>Original Source Span:</b><br>
                    "{p.get('source_span')}"
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# TAB 6: RUN HISTORY & DATABASE
# ==============================================================================
with main_tab6:
    st.subheader("🗄️ Persisted Runs in SQLite Database")
    history_runs = list_runs()

    if not history_runs:
        st.info("No persisted runs found in SQLite database yet.")
    else:
        col_list, col_details = st.columns([1, 2])

        with col_list:
            st.markdown("### Saved Runs")
            for r in history_runs:
                btn_label = f"Run: {r['run_id']} ({r['created_at'][:19]})"
                if st.button(btn_label, key=f"run_btn_{r['run_id']}", use_container_width=True):
                    full_run = get_run(r["run_id"])
                    if full_run:
                        # Reconstruct state structure for inspector
                        st.session_state.current_run = {
                            **full_run,
                            "linkedin_output": full_run.get("generated_outputs", {}).get("linkedin"),
                            "twitter_output": full_run.get("generated_outputs", {}).get("twitter"),
                            "summary_output": full_run.get("generated_outputs", {}).get("summary"),
                            "advisory_output": full_run.get("generated_outputs", {}).get("advisory"),
                            "presentation_output": full_run.get("generated_outputs", {}).get("presentation"),
                            "pptx_path": full_run.get("rendered_assets", {}).get("presentation")
                        }
                        st.rerun()

        with col_details:
            if curr:
                st.markdown(f"### Run Details: `{curr.get('run_id')}`")
                st.json({
                    "run_id": curr.get("run_id"),
                    "created_at": curr.get("created_at"),
                    "tone": curr.get("tone"),
                    "audience": curr.get("audience"),
                    "selected_outputs": curr.get("selected_outputs"),
                    "revision_count": curr.get("revision_count"),
                    "rendered_assets": curr.get("rendered_assets")
                })
                if st.button(f"🗑️ Delete Run {curr.get('run_id')}", type="secondary"):
                    delete_run(curr.get("run_id"))
                    st.session_state.current_run = None
                    st.success("Run deleted from database.")
                    st.rerun()

st.markdown("---")
st.caption("PRISM — Hackathon Edition. Grounded Multi-Channel Synthesis Architecture.")
