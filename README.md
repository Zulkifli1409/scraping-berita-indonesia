# Scraping Web Berita Indonesia

Aplikasi web scraping untuk mengambil artikel berita dari portal berita Indonesia menggunakan Streamlit.

## Fitur

- **Pencarian Multi-Portal**: Scraping artikel dari Kompas.com dan Detik.com
- **Export Data**: Export hasil scraping ke format Excel (.xlsx)
- **Filter Halaman**: Kontrol jumlah halaman yang ingin di-scrape
- **Responsive UI**: Antarmuka modern dan mudah digunakan
- **Real-time Progress**: Monitoring proses scraping secara real-time
- **Statistik**: Menampilkan statistik hasil scraping

## Demo

[Live Demo](https://your-app-name.streamlit.app) _(setelah deploy, ganti dengan URL aplikasi Anda)_

## Persyaratan

- Python 3.8+
- Koneksi internet untuk mengakses portal berita

## Instalasi Lokal

1. Clone repository ini:
```bash
git clone https://github.com/zulkifli1409/scraping-berita-indonesia.git
cd kompas-scraping
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Jalankan aplikasi:
```bash
streamlit run app.py
```

4. Buka browser dan akses `http://localhost:8501`

## Deploy ke Streamlit Cloud

### Langkah 1: Persiapan Repository
1. Push project ini ke GitHub repository Anda
2. Pastikan file `requirements.txt` dan `app.py` ada di root directory

### Langkah 2: Deploy di Streamlit Cloud
1. Kunjungi [share.streamlit.io](https://share.streamlit.io)
2. Login dengan akun GitHub Anda
3. Klik "New app"
4. Pilih repository, branch, dan file utama (`app.py`)
5. Klik "Deploy"

### Langkah 3: Konfigurasi (Opsional)
Jika diperlukan, buat file `.streamlit/config.toml` untuk konfigurasi tambahan:
```toml
[server]
maxUploadSize = 200

[theme]
primaryColor = "#6366f1"
backgroundColor = "#0a0e27"
secondaryBackgroundColor = "#111827"
textColor = "#f9fafb"
```

## Cara Menggunakan

1. **Pilih Portal Berita**: 
    - Kompas.com
    - Detik.com

2. **Masukkan Keyword Pencarian**: 
    - Ketik kata kunci yang ingin dicari (contoh: "ekonomi", "teknologi", "politik")

3. **Tentukan Jumlah Halaman**: 
    - Pilih berapa halaman hasil pencarian yang ingin di-scrape
    - Atau pilih "Semua halaman" untuk scraping semua hasil

4. **Mulai Scraping**: 
    - Klik tombol "Mulai Scraping"
    - Tunggu proses selesai

5. **Lihat Hasil**: 
    - Hasil akan ditampilkan dalam tabel
    - Download hasil dalam format Excel dengan klik tombol download

## Data yang Diambil

### Kompas.com
- Judul artikel
- URL artikel
- Kategori
- Tanggal publikasi
- Deskripsi/snippet

### Detik.com
- Judul artikel
- URL artikel
- Kategori
- Tanggal publikasi
- Deskripsi/snippet

## Struktur Project

```
kompas-scraping/
│
├── app.py              # Aplikasi Streamlit utama
├── kompas.py           # Module scraper untuk Kompas.com
├── detik.py            # Module scraper untuk Detik.com
├── requirements.txt    # Dependencies Python
├── README.md           # Dokumentasi ini
└── .streamlit/         # (Optional) Konfigurasi Streamlit
     └── config.toml
```

## Teknologi yang Digunakan

- **Streamlit**: Framework untuk membuat web app
- **BeautifulSoup4**: Library untuk parsing HTML
- **Requests**: Library untuk HTTP requests
- **Pandas**: Library untuk manipulasi data
- **OpenPyXL**: Library untuk export ke Excel

## Catatan Penting

- Gunakan aplikasi ini dengan bijak dan patuhi Terms of Service dari portal berita
- Scraping yang berlebihan dapat menyebabkan IP Anda diblokir
- Aplikasi ini hanya untuk tujuan edukasi dan penelitian
- Delay antar request sudah diatur untuk menghindari overload server

## Kontribusi

Kontribusi selalu diterima! Silakan:
1. Fork repository ini
2. Buat branch baru (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan Anda (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## License

Project ini dibuat untuk tujuan edukasi. Silakan gunakan dengan bertanggung jawab.

## Author

Dibuat dengan ❤ untuk keperluan scraping berita Indonesia

## Support

Jika ada pertanyaan atau masalah, silakan buat issue di repository ini.

---

Happy Scraping!

