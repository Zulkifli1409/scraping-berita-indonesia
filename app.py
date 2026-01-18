import streamlit as st
import time
import os
from datetime import datetime
from kompas import KompasScraper
from detik import DetikScraper
import pandas as pd

# Konfigurasi Streamlit
st.set_page_config(
    page_title="Scraping Web Berita Indonesia",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Custom - Professional Clean Theme
st.markdown("""
<style>
    /* Import Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background */
    .stApp {
        background-color: #0a0e27;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }
    
    [data-testid="stSidebar"] .stTextInput input {
        background-color: #1f2937;
        color: #f9fafb;
        border: 1px solid #374151;
        border-radius: 6px;
        padding: 0.75rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }
    
    [data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        outline: none;
    }
    
    /* Header */
    .main-header {
        background-color: #111827;
        padding: 2.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #1f2937;
    }
    
    .main-header h1 {
        color: #f9fafb;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
        text-align: center;
    }
    
    .main-header p {
        color: #9ca3af;
        font-size: 0.95rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
        text-align: center;
    }
    
    /* Cards */
    .card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 1.75rem;
        margin: 1rem 0;
        transition: all 0.2s ease;
    }
    
    .card:hover {
        border-color: #374151;
    }
    
    .card h2 {
        color: #f9fafb;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.01em;
    }
    
    .card h3 {
        color: #e5e7eb;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 1.5rem 0 0.75rem 0;
    }
    
    .card p {
        color: #9ca3af;
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 0.25rem 0;
    }
    
    /* Step Box */
    .step-container {
        background-color: #1e1b4b;
        border: 1px solid #312e81;
        border-left: 4px solid #6366f1;
        border-radius: 12px;
        padding: 1.75rem;
        margin: 1.5rem 0;
    }
    
    .step-container h2 {
        color: #e0e7ff;
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }
    
    .step-container p {
        color: #c7d2fe;
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* Alert Boxes */
    .alert-info {
        background-color: #1e3a5f;
        border: 1px solid #2563eb;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        color: #bfdbfe;
        margin: 1rem 0;
    }
    
    .alert-success {
        background-color: #1e4620;
        border: 1px solid #15803d;
        border-left: 4px solid #22c55e;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        color: #bbf7d0;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background-color: #4a3310;
        border: 1px solid #ca8a04;
        border-left: 4px solid #eab308;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        color: #fef08a;
        margin: 1rem 0;
    }
    
    .alert-error {
        background-color: #4c1d1d;
        border: 1px solid #dc2626;
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        color: #fecaca;
        margin: 1rem 0;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #6366f1;
        font-size: 2rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #9ca3af;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
    
    [data-testid="stDataFrame"] {
        background-color: #111827;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #1f2937;
        color: #f9fafb;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 0.65rem 1.5rem;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        letter-spacing: 0.01em;
    }
    
    .stButton button:hover {
        background-color: #374151;
        border-color: #4b5563;
        transform: translateY(-1px);
    }
    
    .stButton button[kind="primary"] {
        background-color: #6366f1;
        color: white;
        border: 1px solid #6366f1;
    }
    
    .stButton button[kind="primary"]:hover {
        background-color: #4f46e5;
        border-color: #4f46e5;
    }
    
    /* Slider */
    .stSlider {
        padding: 1rem 0;
    }
    
    .stSlider [data-baseweb="slider"] {
        padding: 0.5rem 0;
    }
    
    /* Checkbox */
    .stCheckbox {
        color: #e5e7eb;
        padding: 0.5rem 0;
    }
    
    .stCheckbox label {
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #6366f1;
    }
    
    /* Status */
    [data-testid="stStatus"] {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
    }
    
    /* Divider */
    hr {
        border-color: #1f2937;
        margin: 2rem 0;
    }
    
    /* Text elements */
    p, li {
        color: #d1d5db;
    }
    
    h1, h2, h3 {
        color: #f9fafb;
    }
    
    /* Sidebar title */
    [data-testid="stSidebar"] h3 {
        color: #f9fafb;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
    }
    
    /* Info box in sidebar */
    .sidebar-info {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 1rem;
        color: #9ca3af;
        font-size: 0.85rem;
        line-height: 1.6;
    }
    
    .sidebar-info b {
        color: #e5e7eb;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    /* Table styling */
    table {
        font-size: 0.9rem;
    }
    
    thead tr th {
        background-color: #1f2937 !important;
        color: #9ca3af !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.8rem;
        letter-spacing: 0.05em;
    }
    
    tbody tr {
        border-bottom: 1px solid #1f2937;
    }
    
    tbody tr:hover {
        background-color: #1f2937;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #6b7280;
        padding: 2rem 0;
        margin-top: 3rem;
        font-size: 0.85rem;
        border-top: 1px solid #1f2937;
    }
    
    /* Input styling */
    input, textarea {
        font-size: 0.9rem !important;
    }
    
    /* Labels */
    label {
        color: #e5e7eb;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    /* Disable typing in selectbox */
    [data-baseweb="select"] input {
        caret-color: transparent;
        user-select: none;
    }
    
    [data-baseweb="select"] {
        pointer-events: auto;
    }
</style>
""", unsafe_allow_html=True)

# Header
source_name = st.session_state.get('news_source', 'Kompas')

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'keyword' not in st.session_state:
    st.session_state.keyword = ""
if 'total_pages' not in st.session_state:
    st.session_state.total_pages = None
if 'selected_pages' not in st.session_state:
    st.session_state.selected_pages = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'max_articles' not in st.session_state:
    st.session_state.max_articles = None
if 'news_source' not in st.session_state:
    st.session_state.news_source = "Kompas"

# Main Content - Halaman Pencarian
if not st.session_state.keyword:
    # Form Pencarian di halaman utama
    st.markdown("""
    <div class="card" style="max-width: 900px; margin: 2rem auto; padding: 2.5rem;">
        <h2 style="text-align: center; font-size: 2rem; margin-bottom: 0.5rem;">Mulai Scraping Berita</h2>
        <p style="text-align: center; color: #9ca3af; margin-bottom: 2rem;">Pilih sumber berita dan masukkan kata kunci untuk memulai</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Container untuk form
    col1, col2, col3 = st.columns([1, 2.5, 1])
    
    with col2:
        # Pilihan sumber berita
        st.markdown("""
        <div style="background-color: #1f2937; padding: 1.5rem; border-radius: 12px; border: 1px solid #374151; margin-bottom: 1.5rem;">
            <h3 style="color: #f9fafb; margin-bottom: 0.5rem; font-size: 1.1rem;">Pilih Sumber Berita</h3>
            <p style="color: #9ca3af; font-size: 0.85rem; margin: 0;">Pilih website berita yang ingin di-scraping</p>
        </div>
        """, unsafe_allow_html=True)
        
        news_source = st.selectbox(
            "Website Berita",
            options=["Kompas", "Detik", "CNN Indonesia", "Tempo"],
            index=0 if st.session_state.news_source == "Kompas" else (1 if st.session_state.news_source == "Detik" else 0),
            help="Pilih sumber berita yang akan di-scraping",
            label_visibility="collapsed"
        )
        
        # Status ketersediaan
        if news_source in ["Kompas", "Detik"]:
            st.success(f"{news_source} tersedia untuk scraping")
        else:
            st.warning(f"{news_source} segera hadir")
            st.stop()
        
        # Check if news source changed
        if news_source != st.session_state.news_source:
            st.session_state.news_source = news_source
            st.session_state.step = 1
            st.session_state.total_pages = None
            st.session_state.selected_pages = None
            st.session_state.search_results = None
            st.rerun()
        
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        
        # Input keyword
        st.markdown("""
        <div style="background-color: #1f2937; padding: 1.5rem; border-radius: 12px; border: 1px solid #374151; margin-bottom: 1.5rem;">
            <h3 style="color: #f9fafb; margin-bottom: 0.5rem; font-size: 1.1rem;">Masukkan Kata Kunci</h3>
            <p style="color: #9ca3af; font-size: 0.85rem; margin: 0;">Gunakan kata kunci spesifik untuk hasil yang lebih relevan</p>
        </div>
        """, unsafe_allow_html=True)
        
        keyword_input = st.text_input(
            "Kata Kunci Pencarian",
            value=st.session_state.keyword,
            placeholder=f"Contoh: teknologi, ekonomi, politik",
            help=f"Masukkan kata kunci untuk mencari artikel di {news_source}",
            label_visibility="collapsed"
        )
        
        if keyword_input != st.session_state.keyword:
            st.session_state.keyword = keyword_input
            st.session_state.step = 1
            st.session_state.total_pages = None
            st.session_state.selected_pages = None
            st.session_state.search_results = None
            st.rerun()
    
    # Panduan singkat
    st.markdown("<div style='margin: 2.5rem 0;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.markdown("""
        <div class="card">
            <h3 style="text-align: center; margin-bottom: 1.5rem; font-size: 1.3rem;">Cara Penggunaan</h3>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
                <div style="padding: 1.25rem; background-color: #1f2937; border-radius: 8px;">
                    <div style="font-size: 0.9rem; color: #e5e7eb; font-weight: 500; margin-bottom: 0.25rem;">Pilih Website</div>
                    <div style="font-size: 0.75rem; color: #9ca3af;">Kompas atau Detik</div>
                </div>
                <div style="padding: 1.25rem; background-color: #1f2937; border-radius: 8px;">
                    <div style="font-size: 0.9rem; color: #e5e7eb; font-weight: 500; margin-bottom: 0.25rem;">Input Keyword</div>
                    <div style="font-size: 0.75rem; color: #9ca3af;">Cari artikel</div>
                </div>
                <div style="padding: 1.25rem; background-color: #1f2937; border-radius: 8px;">
                    <div style="font-size: 0.9rem; color: #e5e7eb; font-weight: 500; margin-bottom: 0.25rem;">Mulai Scraping</div>
                    <div style="font-size: 0.75rem; color: #9ca3af;">Download hasil</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    # STEP 1: Get total pages
    if st.session_state.step == 1 or st.session_state.total_pages is None:
        st.markdown("""
        <div class="step-container">
            <h2>Langkah 1: Deteksi Halaman Pencarian</h2>
            <p>Menganalisis total halaman yang tersedia untuk kata kunci yang Anda masukkan</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize scraper based on selected news source
        if st.session_state.news_source == "Detik":
            scraper = DetikScraper()
        else:
            scraper = KompasScraper()
        
        with st.status("Mendeteksi halaman pencarian...", expanded=True) as status:
            st.write(f"Menganalisis hasil pencarian untuk: **{st.session_state.keyword}**")
            st.write(f"Sumber: **{st.session_state.news_source}**")
            
            try:
                total_pages = scraper.get_total_search_pages(st.session_state.keyword)
                st.session_state.total_pages = total_pages
                st.write(f"Ditemukan **{total_pages}** halaman hasil pencarian")
                status.update(label=f"Deteksi selesai - {total_pages} halaman tersedia", state="complete", expanded=False)
            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")
                st.stop()
        
        # Tampilkan total halaman tersedia
        st.markdown(f"""
        <div class="alert-info" style="text-align: center; margin-bottom: 1.5rem; font-size: 1.1rem;">
            Total halaman tersedia: <strong style="color: #60a5fa; font-size: 1.3rem;">{st.session_state.total_pages} halaman</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # Input jumlah halaman
        st.markdown("""
        <div style="background-color: #1f2937; padding: 1.5rem; border-radius: 12px; border: 1px solid #374151; margin-bottom: 1rem;">
            <h3 style="color: #f9fafb; margin-bottom: 0.5rem; font-size: 1.1rem;">Masukkan Jumlah Halaman</h3>
            <p style="color: #9ca3af; font-size: 0.85rem; margin: 0;">Masukkan berapa halaman yang ingin di-scan (maks. {0})</p>
        </div>
        """.format(st.session_state.total_pages), unsafe_allow_html=True)
        
        selected_pages = st.number_input(
            "Jumlah Halaman",
            min_value=1,
            max_value=st.session_state.total_pages,
            value=min(5, st.session_state.total_pages),
            step=1,
            help=f"Masukkan jumlah halaman yang ingin di-scan (1 - {st.session_state.total_pages})",
            label_visibility="collapsed"
        )
        st.session_state.selected_pages = selected_pages
        
        if st.button("Lanjutkan ke Pencarian", width="stretch", type="primary"):
            st.session_state.step = 2
            st.rerun()
    
    # STEP 2: Search results
    elif st.session_state.step == 2:
        st.markdown(f"""
        <div class="step-container">
            <h2>Langkah 2: Mengumpulkan Artikel</h2>
            <p>Mengambil daftar artikel dari {st.session_state.selected_pages} halaman pencarian</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Cek apakah search sudah pernah dijalankan
        if st.session_state.search_results is None:
            # Initialize scraper based on selected news source
            if st.session_state.news_source == "Detik":
                scraper = DetikScraper()
            else:
                scraper = KompasScraper()
            
            with st.status("Mengumpulkan artikel...", expanded=True) as status:
                st.write(f"Mencari artikel dengan keyword: **{st.session_state.keyword}**")
                st.write(f"Memproses {st.session_state.selected_pages} halaman...")
                
                try:
                    articles, found_pages = scraper.search_articles(
                        st.session_state.keyword, 
                        max_pages=st.session_state.selected_pages
                    )
                    st.session_state.search_results = articles
                    st.write(f"Berhasil mengumpulkan **{len(articles)}** artikel dari {found_pages} halaman")
                    status.update(label=f"Pengumpulan selesai - {len(articles)} artikel ditemukan", state="complete", expanded=False)
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {str(e)}")
                    st.stop()
        
        # Tampilkan hasil jika sudah ada
        if st.session_state.search_results:
            st.markdown('<div class="card"><h2>Hasil Pencarian</h2></div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Artikel", len(st.session_state.search_results))
            with col2:
                st.metric("Halaman Di-Scan", st.session_state.selected_pages)
            with col3:
                st.metric("Halaman Tersedia", st.session_state.total_pages)
            
            st.markdown('<div class="card"><h3>Daftar Artikel</h3></div>', unsafe_allow_html=True)
            
            articles_list = []
            for i, article in enumerate(st.session_state.search_results, 1):
                articles_list.append({
                    'No': i,
                    'Judul': article.get('title', ''),
                    'Kategori': article.get('category', ''),
                    'Tanggal': article.get('date', '')
                })
            
            df_articles = pd.DataFrame(articles_list)
            st.dataframe(df_articles, width="stretch", hide_index=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Kembali", width="stretch"):
                    st.session_state.step = 1
                    st.rerun()
            
            with col2:
                if st.button("Lanjutkan ke Konfigurasi", width="stretch", type="primary"):
                    st.session_state.step = 3
                    st.rerun()
        else:
            st.markdown('<div class="alert-error">Tidak ada artikel ditemukan</div>', unsafe_allow_html=True)
            if st.button("Kembali", width="stretch"):
                st.session_state.step = 1
                st.rerun()
    
    # STEP 3: Configuration
    elif st.session_state.step == 3:
        st.markdown("""
        <div class="step-container">
            <h2>Langkah 3: Konfigurasi Scraping</h2>
            <p>Atur jumlah artikel dan pengaturan penyimpanan file</p>
        </div>
        """, unsafe_allow_html=True)
        
        total_articles = len(st.session_state.search_results)
        
        # Pemilihan Artikel - More Prominent
        st.markdown("""
        <div class="card">
            <h2>Pemilihan Artikel</h2>
            <p style="margin-top: 0.5rem; color: #9ca3af;">Tentukan berapa artikel yang akan di-scraping</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Info Box dengan styling lebih menonjol
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); 
                    border: 2px solid #3b82f6; 
                    border-radius: 12px; 
                    padding: 1.5rem; 
                    margin: 1.5rem 0;
                    text-align: center;">
            <div style="font-size: 0.9rem; color: #93c5fd; margin-bottom: 0.5rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Total Artikel Tersedia</div>
            <div style="font-size: 3rem; color: #ffffff; font-weight: 700; line-height: 1;">{total_articles}</div>
            <div style="font-size: 0.85rem; color: #bfdbfe; margin-top: 0.5rem;">artikel ditemukan dari pencarian</div>
        </div>
        """, unsafe_allow_html=True)
        
        take_all = st.checkbox(
            "Ambil Semua Artikel",
            value=True,
            help="Nonaktifkan untuk memilih jumlah artikel secara spesifik"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if take_all:
            st.session_state.max_articles = None
            st.markdown(f"""
            <div class="alert-success" style="font-size: 1.05rem; padding: 1.25rem; margin: 1.5rem 0;">
                <strong>✓ Akan mengambil seluruh {total_articles} artikel</strong><br>
                <span style="font-size: 0.9rem; opacity: 0.9;">Semua artikel yang ditemukan akan di-scraping</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Number input dalam container yang lebih menonjol
            st.markdown("""
            <div style="background-color: #1f2937; 
                        border: 2px solid #6366f1; 
                        border-radius: 10px; 
                        padding: 1.5rem; 
                        margin: 1.5rem 0;">
                <div style="color: #e5e7eb; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;">
                    Pilih Jumlah Artikel yang Diinginkan
                </div>
            """, unsafe_allow_html=True)
            
            max_articles_input = st.number_input(
                "Masukkan jumlah artikel",
                min_value=1,
                max_value=total_articles,
                value=min(10, total_articles),
                step=1,
                help=f"Masukkan jumlah artikel yang ingin di-scraping (1 - {total_articles})",
                label_visibility="collapsed"
            )
            st.session_state.max_articles = max_articles_input
            
            st.markdown(f"""
                <div style="text-align: center; margin-top: 1rem; padding: 1rem; background-color: #111827; border-radius: 8px;">
                    <div style="color: #9ca3af; font-size: 0.85rem; margin-bottom: 0.25rem;">Artikel Terpilih</div>
                    <div style="color: #6366f1; font-size: 2rem; font-weight: 700;">{max_articles_input}</div>
                    <div style="color: #9ca3af; font-size: 0.85rem; margin-top: 0.25rem;">dari {total_articles} artikel</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="alert-info" style="font-size: 1.05rem; padding: 1.25rem; margin: 1.5rem 0;">
                <strong>Akan mengambil {max_articles_input} artikel pertama</strong><br>
                <span style="font-size: 0.9rem; opacity: 0.9;">Dari total {total_articles} artikel yang tersedia</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        st.markdown("""
        <div class="card">
            <h2>Pengaturan File</h2>
            <p style="margin-top: 0.5rem; color: #9ca3af;">Tentukan nama file untuk hasil scraping</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Nama file default berdasarkan sumber berita
        default_filename = f"{st.session_state.news_source.lower()}_{st.session_state.keyword}"
        
        custom_filename = st.text_input(
            "Nama File",
            value=default_filename,
            placeholder="Contoh: hasil_scraping",
            help="Nama file tanpa ekstensi, file akan otomatis di-download"
        )
        st.session_state.custom_filename = custom_filename
        
        st.markdown("""
        <div class="alert-info" style="margin: 1rem 0;">
            <strong>File akan otomatis ter-download</strong><br>
            <span style="font-size: 0.9rem;">Setelah scraping selesai, file akan siap untuk di-download</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        st.write("**Format Output**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            save_excel = st.checkbox("Excel (.xlsx)", value=True)
        with col2:
            save_json = st.checkbox("JSON (.json)", value=True)
        with col3:
            save_txt = st.checkbox("Text (.txt)", value=True)
        
        save_formats = []
        if save_excel:
            save_formats.append("Excel (.xlsx)")
        if save_json:
            save_formats.append("JSON (.json)")
        if save_txt:
            save_formats.append("Text (.txt)")
        
        if not save_formats:
            st.markdown('<div class="alert-warning">Pilih minimal satu format penyimpanan</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-success">Format dipilih: {", ".join(save_formats)}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Kembali", width="stretch"):
                st.session_state.step = 2
                st.rerun()
        
        with col2:
            if save_formats and st.button("Mulai Scraping", width="stretch", type="primary"):
                st.session_state.step = 4
                st.session_state.save_formats = save_formats
                st.rerun()
    
    # STEP 4: Scraping
    elif st.session_state.step == 4:
        st.markdown("""
        <div class="step-container">
            <h2>Langkah 4: Proses Scraping</h2>
            <p>Mengekstrak konten lengkap dari setiap artikel</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Cek apakah scraping sudah pernah dijalankan
        if 'scraping_results' not in st.session_state:
            # Initialize scraper based on selected news source
            if st.session_state.news_source == "Detik":
                scraper = DetikScraper()
            else:
                scraper = KompasScraper()
            
            articles_to_process = st.session_state.search_results
            if st.session_state.max_articles:
                articles_to_process = articles_to_process[:st.session_state.max_articles]
            
            with st.status(f"Memproses {len(articles_to_process)} artikel...", expanded=True) as status:
                try:
                    results = []
                    progress_bar = st.progress(0)
                    
                    for idx, article in enumerate(articles_to_process, 1):
                        status.write(f"[{idx}/{len(articles_to_process)}] {article['title'][:60]}...")
                        
                        detail = scraper.get_article_detail(article['url'])
                        
                        if detail:
                            article.update(detail)
                            results.append(article)
                        else:
                            article['content'] = "Gagal mengambil konten"
                            article['author'] = ""
                            article['date_published'] = article['date']
                            article['categories'] = article['category']
                            article['tags'] = ""
                            article['total_pages'] = 1
                            article['multi_page'] = False
                            results.append(article)
                        
                        progress_bar.progress(idx / len(articles_to_process))
                        
                        if idx < len(articles_to_process):
                            time.sleep(1)
                    
                    # Simpan ke temporary files untuk download
                    import tempfile
                    import zipfile
                    from io import BytesIO
                    
                    # Base filename berdasarkan sumber berita
                    default_name = f"{st.session_state.news_source.lower()}_{st.session_state.keyword}"
                    base_filename = st.session_state.custom_filename or default_name
                    
                    files_data = {}
                    
                    if "Excel (.xlsx)" in st.session_state.save_formats:
                        temp_excel = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                        temp_excel.close()  # Close file before using it
                        scraper.save_to_excel(results, temp_excel.name)
                        with open(temp_excel.name, 'rb') as f:
                            files_data['excel'] = {'name': f"{base_filename}.xlsx", 'data': f.read()}
                        try:
                            os.unlink(temp_excel.name)
                        except:
                            pass  # Ignore if file is still locked
                    
                    if "JSON (.json)" in st.session_state.save_formats:
                        temp_json = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode='w', encoding='utf-8')
                        temp_json.close()  # Close file before using it
                        scraper.save_to_json(results, temp_json.name)
                        with open(temp_json.name, 'r', encoding='utf-8') as f:
                            files_data['json'] = {'name': f"{base_filename}.json", 'data': f.read().encode('utf-8')}
                        try:
                            os.unlink(temp_json.name)
                        except:
                            pass  # Ignore if file is still locked
                    
                    if "Text (.txt)" in st.session_state.save_formats:
                        temp_txt = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8')
                        temp_txt.close()  # Close file before using it
                        scraper.save_to_txt(results, temp_txt.name)
                        with open(temp_txt.name, 'r', encoding='utf-8') as f:
                            files_data['txt'] = {'name': f"{base_filename}.txt", 'data': f.read().encode('utf-8')}
                        try:
                            os.unlink(temp_txt.name)
                        except:
                            pass  # Ignore if file is still locked
                    
                    # Buat ZIP file jika lebih dari 1 format
                    if len(files_data) > 1:
                        zip_buffer = BytesIO()
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            for format_type, file_info in files_data.items():
                                zip_file.writestr(file_info['name'], file_info['data'])
                        zip_buffer.seek(0)
                        files_data['zip'] = {
                            'name': f"{base_filename}.zip",
                            'data': zip_buffer.getvalue()
                        }
                    
                    status.update(label="Scraping selesai", state="complete", expanded=False)
                    
                    st.session_state.scraping_results = {
                        'results': results,
                        'files_data': files_data
                    }
                    
                except Exception as e:
                    status.update(label="Terjadi kesalahan", state="error")
                    st.error(f"Error: {str(e)}")
                    st.stop()
        
        # Tampilkan hasil jika sudah ada
        if 'scraping_results' in st.session_state and st.session_state.scraping_results:
            results = st.session_state.scraping_results['results']
            files_data = st.session_state.scraping_results['files_data']
            
            st.markdown(f'<div class="alert-success"><strong>Scraping berhasil diselesaikan</strong><br>Total {len(results)} artikel berhasil diambil</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="card"><h3>Statistik Hasil</h3></div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            content_lengths = [len(article.get('content', '')) for article in results]
            avg_content = sum(content_lengths) / len(content_lengths) if content_lengths else 0
            total_content = sum(content_lengths)
            articles_with_author = sum(1 for a in results if a.get('author'))
            
            with col1:
                st.metric("Total Artikel", len(results))
            with col2:
                st.metric("Dengan Penulis", f"{articles_with_author}")
            with col3:
                st.metric("Rata-rata Konten", f"{avg_content:.0f} chr")
            with col4:
                st.metric("Total Konten", f"{total_content/1000:.1f} KB")
            
            st.markdown("""
            <div class="card">
                <h2>Download Hasil Scraping</h2>
                <p style="margin-top: 0.5rem; color: #9ca3af;">Download semua file hasil scraping dalam satu paket</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Jika lebih dari 1 format, tampilkan download ZIP
            if len(st.session_state.save_formats) > 1 and 'zip' in files_data:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.download_button(
                        label=f"📦 Download Semua File (ZIP)",
                        data=files_data['zip']['data'],
                        file_name=files_data['zip']['name'],
                        mime="application/zip",
                        type="primary",
                        use_container_width=True
                    )
                    
                    # Tampilkan info file yang ada di dalam ZIP
                    formats_text = ", ".join([f.split()[0] for f in st.session_state.save_formats])
                    st.markdown(f"""
                    <div style="text-align: center; margin-top: 1rem; padding: 1rem; background-color: #1f2937; border-radius: 8px;">
                        <p style="color: #9ca3af; margin: 0;">📄 Berisi {len(files_data)-1} file: {formats_text}</p>
                        <p style="color: #9ca3af; margin: 0.5rem 0 0 0; font-size: 0.9rem;">Ukuran: {len(files_data['zip']['data'])/1024:.1f} KB</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Jika hanya 1 format, tampilkan download button biasa
                cols = st.columns(1)
                
                for idx, (format_type, file_info) in enumerate(files_data.items()):
                    if format_type == 'zip':
                        continue
                        
                    with cols[0]:
                        if format_type == 'excel':
                            st.download_button(
                                label="Download Excel",
                                data=file_info['data'],
                                file_name=file_info['name'],
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary",
                                use_container_width=True
                            )
                        elif format_type == 'json':
                            st.download_button(
                                label="Download JSON",
                                data=file_info['data'],
                                file_name=file_info['name'],
                                mime="application/json",
                                type="primary",
                                use_container_width=True
                            )
                        elif format_type == 'txt':
                            st.download_button(
                                label="Download Text",
                                data=file_info['data'],
                                file_name=file_info['name'],
                                mime="text/plain",
                                type="primary",
                                use_container_width=True
                            )
                        
                        file_size = len(file_info['data']) / 1024
                        st.markdown(f"""
                        <div style="text-align: center; margin-top: 0.5rem;">
                            <p style="color: #9ca3af; font-size: 0.9rem; margin: 0;">{file_info['name']} ({file_size:.1f} KB)</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.divider()
            
            st.markdown('<div class="card"><h3>Preview Data</h3></div>', unsafe_allow_html=True)
            
            preview_data = []
            for i, article in enumerate(results[:10], 1):
                preview_data.append({
                    'No': i,
                    'Judul': article.get('title', '')[:60] + '...',
                    'Penulis': article.get('author', '-')[:25],
                    'Tanggal': article.get('date_published', ''),
                    'Konten': f"{len(article.get('content', ''))} chr"
                })
            
            df_preview = pd.DataFrame(preview_data)
            st.dataframe(df_preview, width="stretch", hide_index=True)
            
            if len(results) > 10:
                st.markdown(f'<div class="alert-info">Menampilkan 10 dari {len(results)} artikel</div>', unsafe_allow_html=True)
            
            st.divider()
            
            # Tombol kembali ke home
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if st.button("Selesai - Kembali ke Home", width="stretch", type="primary"):
                    # Reset semua session state
                    st.session_state.step = 0
                    st.session_state.keyword = ""
                    st.session_state.total_pages = None
                    st.session_state.selected_pages = None
                    st.session_state.search_results = None
                    st.session_state.max_articles = None
                    st.session_state.scraping_results = None
                    st.rerun()

st.divider()
st.markdown("""
<div class="footer">
    Scraping Web Berita Indonesia | Dibuat karena gabut © 2026
</div>
""", unsafe_allow_html=True)