"""
Société Générale branding styles for Streamlit UI.
Colors: white background, dark text, red for filters/actions (SG red #E2001A)
"""

SG_CSS = """
<style>
:root {
    --sg-red: #E2001A;
    --sg-black: #000000;
    --sg-dark: #1a1a1a;
    --sg-white: #FFFFFF;
    --sg-gray-light: #E0E0E0;
    --sg-gray-medium: #6C757D;
    --sg-success: #28A745;
    --sg-warning: #FFC107;
    --sg-error: #DC3545;
    --sg-info: #0066CC;
}

/* Primary buttons */
.stButton>button {
    background-color: var(--sg-red);
    color: var(--sg-white);
    border: none;
    border-radius: 4px;
    font-weight: 500;
    transition: background-color 0.3s;
}

.stButton>button:hover {
    background-color: #C00015;
    color: var(--sg-white);
}

/* Secondary buttons */
.stButton>button[kind="secondary"] {
    background-color: var(--sg-white);
    color: var(--sg-red);
    border: 1px solid var(--sg-red);
}

.stButton>button[kind="secondary"]:hover {
    background-color: var(--sg-red);
    color: var(--sg-white);
}

/* Status badges */
.badge-success {
    background-color: var(--sg-success);
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
    display: inline-block;
}

.badge-warning {
    background-color: var(--sg-warning);
    color: var(--sg-black);
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
    display: inline-block;
}

.badge-error {
    background-color: var(--sg-error);
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
    display: inline-block;
}

.badge-info {
    background-color: var(--sg-info);
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
    display: inline-block;
}

/* Keyword tags */
.keyword-tag {
    background-color: #F5F5F5;
    color: var(--sg-black);
    border: 1px solid rgba(226, 0, 26, 0.3);
    padding: 4px 10px;
    border-radius: 16px;
    font-size: 0.85rem;
    display: inline-block;
    margin: 2px;
}

/* Document card */
.document-card {
    background-color: var(--sg-white);
    border: 1px solid var(--sg-gray-light);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: box-shadow 0.3s;
}

.document-card:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* Authority badges */
.authority-bcl {
    background-color: #0066CC;
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
}

.authority-ecb {
    background-color: #FFD700;
    color: var(--sg-black);
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
}

.authority-other {
    background-color: var(--sg-gray-medium);
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
}

/* Links */
a {
    color: var(--sg-red);
    text-decoration: none;
}

a:hover {
    color: #C00015;
    text-decoration: underline;
}

/* Main title */
h1 {
    color: var(--sg-black);
}

/* Metrics */
[data-testid="stMetricValue"] {
    color: var(--sg-black);
}

[data-testid="stMetricLabel"] {
    color: var(--sg-gray-medium);
}

/* Main background - white */
.main .block-container {
    background-color: var(--sg-white) !important;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Sidebar background - white */
[data-testid="stSidebar"] {
    background-color: var(--sg-white) !important;
}

/* Sidebar header - red background for filters section */
[data-testid="stSidebar"] .stHeader {
    background-color: var(--sg-red) !important;
    color: var(--sg-white) !important;
    padding: 0.5rem;
    border-radius: 4px;
    margin-bottom: 1rem;
}

/* Filter sections in sidebar - red background */
[data-testid="stSidebar"] .stSubheader {
    background-color: rgba(226, 0, 26, 0.1) !important;
    color: var(--sg-red) !important;
    font-weight: 600;
    border-bottom: 2px solid var(--sg-red);
    padding: 0.5rem;
    border-radius: 4px;
    margin-bottom: 0.5rem;
}

/* Selectboxes in sidebar - red background */
[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: rgba(226, 0, 26, 0.1) !important;
}

[data-testid="stSidebar"] .stSelectbox label {
    color: var(--sg-red) !important;
    font-weight: 600;
}

/* Checkboxes in sidebar - red accent */
[data-testid="stSidebar"] .stCheckbox label {
    color: var(--sg-red) !important;
}

/* Text inputs in sidebar */
[data-testid="stSidebar"] .stTextInput > div > div > input {
    border-color: var(--sg-red) !important;
}

[data-testid="stSidebar"] .stTextInput label {
    color: var(--sg-red) !important;
    font-weight: 600;
}

/* Text areas in sidebar */
[data-testid="stSidebar"] .stTextArea > div > div > textarea {
    border-color: var(--sg-red) !important;
}

[data-testid="stSidebar"] .stTextArea label {
    color: var(--sg-red) !important;
    font-weight: 600;
}

/* Cards background - white */
.document-card {
    background-color: var(--sg-white);
    border: 1px solid var(--sg-gray-light);
}

/* Table headers - red background */
thead th {
    background-color: var(--sg-red) !important;
    color: var(--sg-white) !important;
}

/* Ensure all text is dark on white background */
p, span, div, h1, h2, h3, h4, h5, h6 {
    color: var(--sg-black);
}

/* Links remain red */
a {
    color: var(--sg-red);
}

/* Body and app background - white */
body {
    background-color: var(--sg-white) !important;
}

.stApp {
    background-color: var(--sg-white) !important;
}

/* Remove any dark backgrounds from Streamlit elements */
[data-testid="stAppViewContainer"] {
    background-color: var(--sg-white) !important;
}

[data-testid="stHeader"] {
    background-color: var(--sg-white) !important;
}

/* Main content area - white */
section[data-testid="stSidebar"] > div {
    background-color: var(--sg-white) !important;
}

/* Tabs - white background */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--sg-white) !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: var(--sg-white) !important;
    color: var(--sg-black) !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: rgba(226, 0, 26, 0.1) !important;
}

.stTabs [aria-selected="true"] {
    background-color: var(--sg-white) !important;
    color: var(--sg-red) !important;
    border-bottom: 2px solid var(--sg-red) !important;
}

/* Expanders - white background */
.streamlit-expanderHeader {
    background-color: var(--sg-white) !important;
    color: var(--sg-black) !important;
}

.streamlit-expanderContent {
    background-color: var(--sg-white) !important;
}

/* Code blocks - light background */
.stCodeBlock {
    background-color: #F5F5F5 !important;
}

/* Info boxes - light background */
.stAlert {
    background-color: #F5F5F5 !important;
}

/* Success/Error boxes - light backgrounds */
div[data-baseweb="notification"] {
    background-color: var(--sg-white) !important;
}

/* Dataframe tables - white background */
.dataframe {
    background-color: var(--sg-white) !important;
}

/* Input fields - white background */
input, textarea, select {
    background-color: var(--sg-white) !important;
    color: var(--sg-black) !important;
}

/* Remove any dark theme remnants */
[data-theme="dark"] {
    display: none !important;
}

/* Multi-select in sidebar - red background */
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background-color: rgba(226, 0, 26, 0.1) !important;
}

[data-testid="stSidebar"] .stMultiSelect label {
    color: var(--sg-red) !important;
    font-weight: 600;
}

/* Time input in sidebar */
[data-testid="stSidebar"] .stTimeInput label {
    color: var(--sg-red) !important;
    font-weight: 600;
}

/* Number input in sidebar */
[data-testid="stSidebar"] .stNumberInput label {
    color: var(--sg-red) !important;
    font-weight: 600;
}

/* Remove any dark backgrounds from Streamlit elements */
[data-testid="stAppViewContainer"] {
    background-color: var(--sg-white) !important;
}

[data-testid="stHeader"] {
    background-color: var(--sg-white) !important;
}

/* Main content area - white */
section[data-testid="stSidebar"] > div {
    background-color: var(--sg-white) !important;
}

/* Tabs - white background */
.stTabs [data-baseweb="tab-list"] {
    background-color: var(--sg-white) !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: var(--sg-white) !important;
    color: var(--sg-black) !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background-color: rgba(226, 0, 26, 0.1) !important;
}

.stTabs [aria-selected="true"] {
    background-color: var(--sg-white) !important;
    color: var(--sg-red) !important;
    border-bottom: 2px solid var(--sg-red) !important;
}

/* Expanders - white background */
.streamlit-expanderHeader {
    background-color: var(--sg-white) !important;
    color: var(--sg-black) !important;
}

.streamlit-expanderContent {
    background-color: var(--sg-white) !important;
}

/* Code blocks - light background */
.stCodeBlock {
    background-color: #F5F5F5 !important;
}

/* Info boxes - light background */
.stAlert {
    background-color: #F5F5F5 !important;
}

/* Success/Error boxes - light backgrounds */
div[data-baseweb="notification"] {
    background-color: var(--sg-white) !important;
}

/* Dataframe tables - white background */
.dataframe {
    background-color: var(--sg-white) !important;
}

/* Input fields - white background */
input, textarea, select {
    background-color: var(--sg-white) !important;
    color: var(--sg-black) !important;
}

/* Remove any dark theme remnants */
[data-theme="dark"] {
    display: none !important;
}

/* Force white background on all Streamlit containers */
div[class*="st"] {
    background-color: var(--sg-white) !important;
}

/* Text areas and code areas - white */
.stTextArea textarea, .stCodeBlock pre {
    background-color: var(--sg-white) !important;
    color: var(--sg-black) !important;
}

/* Metrics containers - white */
[data-testid="stMetricContainer"] {
    background-color: var(--sg-white) !important;
}

/* Columns - white */
[data-testid="column"] {
    background-color: var(--sg-white) !important;
}

/* Containers - white */
[data-testid="stVerticalBlock"] {
    background-color: var(--sg-white) !important;
}

/* Override with white for all main elements */
body, .stApp, [data-testid="stAppViewContainer"], 
.main, [data-testid="stSidebar"], 
[data-testid="stVerticalBlock"],
div[class*="element-container"],
div[class*="stMarkdown"],
div[class*="stText"] {
    background-color: var(--sg-white) !important;
}

/* Force white on all Streamlit widgets */
.stSelectbox, .stTextInput, .stTextArea, 
.stCheckbox, .stRadio, .stSlider,
.stNumberInput, .stTimeInput, .stDateInput {
    background-color: var(--sg-white) !important;
}

/* Remove dark backgrounds from any element */
div, section, article, main, aside {
    background-color: var(--sg-white) !important;
}
</style>
"""


def apply_sg_styles():
    """Apply Société Générale styles to Streamlit."""
    import streamlit as st
    st.markdown(SG_CSS, unsafe_allow_html=True)

