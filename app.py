"""
Streamlit UI for Smart Regulatory Watch Tool
Société Générale Branding - White background, Dark text, Red for filters

Security:
- No secrets in code (all in .env)
- No sensitive content logging
- File validation before processing
- Secure error handling
"""

import streamlit as st
import os
import sys
from datetime import datetime
import importlib

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force reload modules to avoid caching issues
if 'main' in sys.modules:
    importlib.reload(sys.modules['main'])
if 'agents.translation_agent' in sys.modules:
    importlib.reload(sys.modules['agents.translation_agent'])

from core.state import PipelineState
from core.logging_utils import logger
from main import run_pipeline, DEFAULT_KEYWORDS
from agents.scheduler_agent import start_scheduler, schedule_daily_job, get_scheduled_jobs, stop_scheduler
from utils.keywords_loader import load_keywords_from_excel
from utils.document_retriever import get_recent_documents, get_document_keywords_summary, get_file_type
from utils.agent_status import get_agent_status_from_logs, get_agent_status_from_pipeline_result
from utils.storage import get_session, RunLog
from ui.sg_styles import apply_sg_styles


# ======================================================
# PAGE CONFIGURATION
# ======================================================

st.set_page_config(
    page_title="Regulatory Watch Tool - Société Générale",
    page_icon="📘",
    layout="wide"
)

# Apply SG branding styles
apply_sg_styles()

# ======================================================
# SESSION STATE INITIALIZATION
# ======================================================

if "user_keywords" not in st.session_state:
    st.session_state.user_keywords = []

if "pipeline_results" not in st.session_state:
    st.session_state.pipeline_results = None

if "scheduler_running" not in st.session_state:
    st.session_state.scheduler_running = False


# ======================================================
# SIDEBAR CONFIGURATION
# ======================================================

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Regulator selection
    regulator = st.selectbox(
        "Select Regulator",
        ["BCL", "ECB", "Bundesbank"],
        index=0
    )
    
    # Translation toggle
    enable_translation = st.checkbox("Enable Translation (Gemini)", value=True)
    
    # Notification toggle
    enable_notification = st.checkbox("Enable Email Notifications", value=False)
    
    if enable_notification:
        email_recipients = st.text_area(
            "Email Recipients (one per line)",
            value="",
            help="Enter email addresses, one per line"
        )
        email_list = [e.strip() for e in email_recipients.split("\n") if e.strip()]
    else:
        email_list = []
    
    # Keyword settings
    st.subheader("Keywords")
    send_only_if_keywords = st.checkbox(
        "Send email only if keywords found",
        value=True
    )
    
    # Scheduler settings
    st.subheader("Scheduler")
    schedule_time = st.time_input("Daily run time", value=datetime.strptime("08:00", "%H:%M").time())
    
    if st.button("Start Scheduler"):
        if not st.session_state.scheduler_running:
            start_scheduler()
            schedule_daily_job(
                lambda: run_pipeline(regulator=regulator),
                time_str=schedule_time.strftime("%H:%M")
            )
            st.session_state.scheduler_running = True
            st.success("Scheduler started!")
        else:
            st.warning("Scheduler is already running.")
    
    if st.button("Stop Scheduler"):
        if st.session_state.scheduler_running:
            stop_scheduler()
            st.session_state.scheduler_running = False
            st.success("Scheduler stopped!")
        else:
            st.warning("Scheduler is not running.")


# ======================================================
# HEADER WITH SG LOGO
# ======================================================

col_logo, col_title = st.columns([0.1, 0.9])
with col_logo:
    # Try to load SG logo, fallback to text if not found
    logo_path = os.path.join("assets", "sg_logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=70)
    else:
        # Fallback: try from downloads
        alt_logo = os.path.join(os.path.expanduser("~"), "Downloads", "hamza", "datathon", "streamlit-main", "societe-generale-logo-png_seeklogo-288573.png")
        if os.path.exists(alt_logo):
            st.image(alt_logo, width=70)
        else:
            st.markdown("**SG**")  # Text fallback

with col_title:
    st.title("Regulatory Watch Tool")

st.markdown("---")

# ======================================================
# DASHBOARD - VUE D'ENSEMBLE
# ======================================================

st.markdown("## 📊 Dashboard – Vue d'ensemble")

# Load documents from database for KPIs
try:
    recent_docs = get_recent_documents(limit=100)
    total_docs = len(recent_docs)
    
    # Count keywords (from all documents)
    total_keywords = 0
    for doc in recent_docs:
        kw_summary = get_document_keywords_summary(doc.id)
        total_keywords += len(kw_summary)
    
    # Count notifications from RunLog
    try:
        from sqlmodel import select
        session = get_session()
        notification_logs = session.exec(
            select(RunLog).where(RunLog.status == "ok")
        ).all()
        notifications_sent = len(notification_logs)
        session.close()
    except Exception:
        notifications_sent = 0
    
except Exception as e:
    logger.error(f"Error loading dashboard data: {type(e).__name__}")
    total_docs = 0
    total_keywords = 0
    notifications_sent = 0

# KPIs
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric("📄 Documents analysés", total_docs)
with kpi2:
    st.metric("🔑 Mots-clés détectés", total_keywords)
with kpi3:
    st.metric("📬 Notifications envoyées", notifications_sent)

# Agent Status (from real pipeline execution)
st.markdown("### 🤖 Statut des Agents d'Analyse")

# Get status from pipeline result (if available) or from logs
agent_status = {}
if st.session_state.pipeline_results:
    agent_status = get_agent_status_from_pipeline_result(st.session_state.pipeline_results)
else:
    agent_status = get_agent_status_from_logs()

agent_cols = st.columns(4)

# Extraction
with agent_cols[0]:
    st.markdown("**Extraction**")
    if agent_status.get("Extraction") == "ok":
        st.success("✅ OK")
    elif agent_status.get("Extraction") == "error":
        st.error("❌ Erreur")
    elif agent_status.get("Extraction") == "running":
        st.info("⏳ En cours")
    else:
        st.info("⏳ En attente")

# Traduction
with agent_cols[1]:
    st.markdown("**Traduction**")
    if agent_status.get("Traduction") == "ok":
        st.success("✅ OK")
    elif agent_status.get("Traduction") == "error":
        st.error("❌ Erreur")
    elif agent_status.get("Traduction") == "running":
        st.info("⏳ En cours")
    else:
        st.info("⏳ En attente")

# Analyse
with agent_cols[2]:
    st.markdown("**Analyse**")
    if agent_status.get("Analyse") == "ok":
        st.success("✅ OK")
    elif agent_status.get("Analyse") == "error":
        st.error("❌ Erreur")
    elif agent_status.get("Analyse") == "running":
        st.info("⏳ En cours")
    else:
        st.info("⏳ En attente")

# Notification
with agent_cols[3]:
    st.markdown("**Notification**")
    if agent_status.get("Notification") == "ok":
        st.success("✅ OK")
    elif agent_status.get("Notification") == "error":
        st.error("❌ Erreur")
    elif agent_status.get("Notification") == "running":
        st.info("⏳ En cours")
    else:
        st.info("⏳ En attente")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Documents analysés", "Run Pipeline", "Keywords", "Results", "Logs"])


# ======================================================
# TAB 1: DOCUMENTS ANALYSÉS (CARDS - OPTION B)
# ======================================================

with tab1:
    st.header("📄 Documents analysés / Document Analyzer")
    
    # Load documents from database
    try:
        documents = get_recent_documents(limit=50)
        
        if documents:
            # Display in grid of cards
            num_cols = 2
            for i in range(0, len(documents), num_cols):
                cols = st.columns(num_cols)
                for j, doc in enumerate(documents[i:i+num_cols]):
                    with cols[j]:
                        # Card container
                        with st.container():
                            # Title (truncated)
                            title = doc.title[:60] + "..." if len(doc.title) > 60 else doc.title
                            st.markdown(f"### 📄 {title}")
                            
                            # Metadata row
                            meta_col1, meta_col2, meta_col3 = st.columns(3)
                            with meta_col1:
                                # Authority badge
                                auth_id = doc.authority_id.upper()
                                if auth_id == "BCL":
                                    st.markdown('<span class="authority-bcl">BCL</span>', unsafe_allow_html=True)
                                elif auth_id == "ECB":
                                    st.markdown('<span class="authority-ecb">ECB</span>', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<span class="authority-other">{auth_id}</span>', unsafe_allow_html=True)
                            
                            with meta_col2:
                                # Date
                                date_str = doc.published_at.strftime("%Y-%m-%d") if doc.published_at else doc.fetched_at.strftime("%Y-%m-%d")
                                st.markdown(f"📅 {date_str}")
                            
                            with meta_col3:
                                # File type
                                file_type = get_file_type(doc.content_path)
                                st.markdown(f"📎 {file_type.upper()}")
                            
                            # Keywords detected
                            kw_summary = get_document_keywords_summary(doc.id)
                            total_kw = len(kw_summary)
                            st.markdown(f"**🔑 {total_kw} keywords detected**")
                            
                            # Keyword tags (first 5)
                            if kw_summary:
                                kw_tags = list(kw_summary.keys())[:5]
                                tags_html = " ".join([f'<span class="keyword-tag">{kw}</span>' for kw in kw_tags])
                                if total_kw > 5:
                                    tags_html += f' <span class="keyword-tag">+{total_kw - 5} more</span>'
                                st.markdown(tags_html, unsafe_allow_html=True)
                            
                            # Status badges (simplified - would need actual agent status)
                            status_cols = st.columns(4)
                            with status_cols[0]:
                                st.markdown('<span class="badge-success">✅ Extraction</span>', unsafe_allow_html=True)
                            with status_cols[1]:
                                st.markdown('<span class="badge-success">✅ Translation</span>', unsafe_allow_html=True)
                            with status_cols[2]:
                                st.markdown('<span class="badge-info">⏳ Analysis</span>', unsafe_allow_html=True)
                            with status_cols[3]:
                                st.markdown('<span class="badge-error">❌ Notification</span>', unsafe_allow_html=True)
                            
                            # Actions
                            action_col1, action_col2 = st.columns(2)
                            with action_col1:
                                if st.button("Voir le détail", key=f"detail_{doc.id}", use_container_width=True):
                                    st.session_state[f"show_detail_{doc.id}"] = True
                            
                            with action_col2:
                                if st.button("Ouvrir source", key=f"source_{doc.id}", use_container_width=True):
                                    st.markdown(f"[Open in browser]({doc.url})", unsafe_allow_html=True)
                            
                            # Detail modal (expander)
                            if st.session_state.get(f"show_detail_{doc.id}", False):
                                with st.expander("📋 Détails complets", expanded=True):
                                    st.markdown(f"**Titre complet:** {doc.title}")
                                    st.markdown(f"**URL source:** [{doc.url}]({doc.url})")
                                    st.markdown(f"**Date de publication:** {doc.published_at.strftime('%Y-%m-%d %H:%M') if doc.published_at else 'N/A'}")
                                    st.markdown(f"**Date de détection:** {doc.fetched_at.strftime('%Y-%m-%d %H:%M')}")
                                    st.markdown(f"**Hash SHA-256:** `{doc.hash[:16]}...` (for verification)")
                                    st.markdown(f"**Chemin local:** `{doc.content_path}`")
                                    
                                    # Keywords by language (if available)
                                    if kw_summary:
                                        st.markdown("**Mots-clés détectés:**")
                                        for kw, count in kw_summary.items():
                                            st.markdown(f"- **{kw}**: {count} occurrence(s)")
                                    
                                    # Summary if available
                                    if doc.translated_path and os.path.exists(doc.translated_path):
                                        try:
                                            with open(doc.translated_path, "r", encoding="utf-8") as f:
                                                summary = f.read()[:500]
                                                st.markdown("**Résumé traduit:**")
                                                st.write(summary + "...")
                                        except:
                                            pass
                            
                            st.markdown("---")
        else:
            st.info("Aucun document analysé pour le moment. Exécutez le pipeline pour commencer.")
    
    except Exception as e:
        logger.error(f"Error displaying documents: {type(e).__name__}")
        st.error("Erreur lors du chargement des documents. Vérifiez les logs.")


# ======================================================
# TAB 2: RUN PIPELINE
# ======================================================

with tab1:
    st.header("Execute Pipeline")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Load keywords from file
        try:
            excel_keywords = load_keywords_from_excel()
            if excel_keywords:
                all_keywords = list(set(DEFAULT_KEYWORDS + excel_keywords))
                st.info(f"✅ Loaded {len(excel_keywords)} keywords")
            else:
                all_keywords = DEFAULT_KEYWORDS
                st.warning("⚠️ Could not load keywords from file. Using defaults.")
        except Exception as e:
            logger.error(f"Error loading keywords: {type(e).__name__}")
            all_keywords = DEFAULT_KEYWORDS
            st.warning("⚠️ Using default keywords only.")
        
        predefined_keywords_input = st.text_area(
            "Predefined Keywords (one per line)",
            value="\n".join(all_keywords[:50]),  # Show first 50
            height=150,
            help="Keywords loaded from Key Words.xlsx + defaults"
        )
        predefined_keywords = [k.strip() for k in predefined_keywords_input.split("\n") if k.strip()]
    
    with col2:
        user_keywords_input = st.text_area(
            "User-Defined Keywords (one per line)",
            value="\n".join(st.session_state.user_keywords),
            height=150
        )
        user_keywords = [k.strip() for k in user_keywords_input.split("\n") if k.strip()]
        st.session_state.user_keywords = user_keywords
    
    st.subheader("File & Language Selection")
    
    col_file, col_lang = st.columns(2)
    
    with col_file:
        # Get list of available files
        import os
        downloads_dir = os.path.join("data", "downloads")
        available_files = []
        if os.path.exists(downloads_dir):
            for file in os.listdir(downloads_dir):
                file_path = os.path.join(downloads_dir, file)
                if os.path.isfile(file_path) and not file.startswith("."):
                    available_files.append(file_path)
        
        if available_files:
            selected_file = st.selectbox(
                "Select file to process (optional)",
                options=["Auto (new documents only)"] + sorted(available_files),
                help="Choose a specific file to process, or 'Auto' to process only new documents"
            )
            if selected_file == "Auto (new documents only)":
                selected_file = None
        else:
            selected_file = None
            st.info("No files found in downloads folder")
    
    with col_lang:
        target_language = st.selectbox(
            "Target language for translation",
            options=["French", "English", "German", "Spanish", "Italian", "Portuguese", "Dutch", "Romanian"],
            index=0,
            help="Language to translate documents into using Gemini"
        )
    
    # Force process option
    force_process = st.checkbox(
        "Force process selected file (even if unchanged)",
        value=False,
        help="Process the selected file even if it hasn't changed"
    )
    
    if st.button("🚀 Run Pipeline Now", type="primary", use_container_width=True):
        with st.spinner("Running pipeline... This may take a few minutes."):
            try:
                result = run_pipeline(
                    regulator=regulator,
                    predefined_keywords=predefined_keywords,
                    user_keywords=user_keywords,
                    enable_translation=enable_translation,
                    enable_notification=enable_notification and len(email_list) > 0,
                    send_only_if_keywords=send_only_if_keywords,
                    email_recipients=email_list if enable_notification else None,
                    force_process_existing=force_process or (selected_file is not None),
                    selected_file=selected_file,
                    target_language=target_language
                )
                
                st.session_state.pipeline_results = result
                
                if result.errors:
                    st.error(f"Pipeline completed with {len(result.errors)} error(s)")
                    for error in result.errors:
                        st.error(f"  - {error}")
                else:
                    st.success("✅ Pipeline completed successfully!")
                    
                    # Show summary
                    st.info(f"**Files processed:** {len(result.file_paths)}")
                    st.info(f"**Keywords found:** {len(result.keyword_hits)}")
                    
            except Exception as e:
                st.error(f"Pipeline failed: {e}")
                logger.error(f"Pipeline error: {e}", exc_info=True)


# ======================================================
# TAB 3: KEYWORDS
# ======================================================

with tab3:
    st.header("Keyword Management")
    
    st.subheader("Current Keywords")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Predefined Keywords:**")
        for kw in DEFAULT_KEYWORDS:
            st.write(f"- {kw}")
    
    with col2:
        st.write("**User-Defined Keywords:**")
        if st.session_state.user_keywords:
            for kw in st.session_state.user_keywords:
                st.write(f"- {kw}")
        else:
            st.write("_No user keywords defined_")
    
    # Add new keyword
    st.subheader("Add Keyword")
    new_keyword = st.text_input("Enter new keyword")
    if st.button("Add Keyword"):
        if new_keyword.strip() and new_keyword.strip() not in st.session_state.user_keywords:
            st.session_state.user_keywords.append(new_keyword.strip())
            st.success(f"Added: {new_keyword}")
            st.rerun()


# ======================================================
# TAB 4: RESULTS
# ======================================================

with tab4:
    st.header("Pipeline Results")
    
    if st.session_state.pipeline_results:
        result = st.session_state.pipeline_results
        
        st.subheader("Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Regulator", result.regulator)
        with col2:
            st.metric("Files Processed", len(result.file_paths))
        with col3:
            st.metric("Keywords Found", len(result.keyword_hits))
        
        # Version Analysis
        st.subheader("📊 Version Analysis")
        try:
            import json
            versions_file = os.path.join("data", "versions.json")
            if os.path.exists(versions_file):
                with open(versions_file, "r", encoding="utf-8") as f:
                    versions = json.load(f)
                
                if versions:
                    st.write(f"**Total tracked documents:** {len(versions)}")
                    
                    # Show recent versions
                    st.write("**Recent document versions:**")
                    version_items = list(versions.items())[-3:]  # Last 3
                    for url, hash_value in reversed(version_items):
                        # Truncate URL for display
                        display_url = url[:80] + "..." if len(url) > 80 else url
                        st.write(f"- `{display_url}`")
                        st.code(f"Hash: {hash_value[:16]}...", language=None)
                else:
                    st.info("No versions tracked yet.")
            else:
                st.info("Version tracking file not found. Run extraction to start tracking.")
        except Exception as e:
            logger.error(f"Error loading versions: {type(e).__name__}")
            st.warning("Could not load version information.")
        
        st.markdown("---")
        
        # Show keyword hits
        if result.keyword_hits:
            st.subheader("Keyword Matches")
            for keyword, contexts in result.keyword_hits.items():
                with st.expander(f"🔍 {keyword} ({len(contexts)} match(es))"):
                    for i, context in enumerate(contexts[:5], 1):  # Show first 5
                        st.write(f"**Match {i}:**")
                        st.code(context[:300] + "..." if len(context) > 300 else context)
        
        # Show file paths
        if result.file_paths:
            st.subheader("Processed Files")
            for file_path in result.file_paths[:10]:  # Show first 10
                st.write(f"- `{file_path}`")
        
        # Show summary/translation (from Gemini)
        if hasattr(result, 'summary') and result.summary:
            st.subheader("Document Summary (Translated by Gemini)")
            st.write(result.summary)
        
    else:
        st.info("No pipeline results yet. Run the pipeline first.")


# ======================================================
# TAB 5: LOGS
# ======================================================

with tab5:
    st.header("System Logs")
    
    # Show recent log entries
    log_file = f"data/logs/reg_watch_{datetime.now().strftime('%Y-%m-%d')}.log"
    
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            st.text_area(
                "Today's Logs",
                value="".join(lines[-50:]),  # Last 50 lines
                height=400
            )
    else:
        st.info("No log file found for today.")
    
    # Scheduler status
    st.subheader("Scheduler Status")
    if st.session_state.scheduler_running:
        st.success("✅ Scheduler is running")
        jobs = get_scheduled_jobs()
        if jobs:
            st.write("**Scheduled Jobs:**")
            for job in jobs:
                st.write(f"- {job}")
    else:
        st.info("Scheduler is not running")


# ======================================================
# FOOTER
# ======================================================

st.markdown("---")
st.markdown(
    "<small>Smart Regulatory Watch Tool - Datathon SG GSC × MBA ESG | Powered by Gemini AI</small>",
    unsafe_allow_html=True
)
