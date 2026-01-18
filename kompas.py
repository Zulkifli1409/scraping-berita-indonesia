"""
Kompas Scraper Module
Library untuk scraping artikel dari Kompas.com
"""

import requests
from bs4 import BeautifulSoup
import time
import json
import re
import pandas as pd
from urllib.parse import urljoin
import warnings
import os
from pathlib import Path
warnings.filterwarnings('ignore')

class KompasScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        self.base_search_url = "https://search.kompas.com/search"
    
    def get_total_search_pages(self, keyword):
        """Mendapatkan total halaman pencarian tanpa mengambil artikel"""
        try:
            params = {'q': keyword, 'page': 1}
            response = self.session.get(self.base_search_url, params=params, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            total_pages = self.get_total_pages(soup)
            return total_pages if total_pages else 1
        except Exception as e:
            print(f"Error mendapatkan total halaman: {e}")
            return 1
        
    def search_articles(self, keyword, max_pages=None):
        """Mencari artikel berdasarkan keyword dengan pagination yang benar"""
        articles = []
        page = 1
        total_pages = None
        
        print(f"[SEARCHING] Memulai pencarian untuk keyword: {keyword}")
        
        while True:
            # Cek jika sudah mencapai batas halaman yang diinginkan
            if max_pages and page > max_pages:
                break
                
            params = {
                'q': keyword,
                'page': page
            }
            
            try:
                print(f"Mengambil halaman {page}...")
                response = self.session.get(self.base_search_url, params=params, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Cari semua artikel
                article_items = soup.find_all('div', class_='articleItem')
                
                if not article_items:
                    print("Tidak ditemukan artikel di halaman ini")
                    break
                
                print(f"Ditemukan {len(article_items)} artikel di halaman {page}")
                
                for item in article_items:
                    article_data = self.extract_search_result(item)
                    if article_data:
                        articles.append(article_data)
                
                # Cek total halaman dari pagination
                if total_pages is None:
                    total_pages = self.get_total_pages(soup)
                
                # Cek apakah ada halaman berikutnya
                if page >= total_pages:
                    print("Sudah sampai halaman terakhir")
                    break
                    
                page += 1
                time.sleep(1.5)  # Delay untuk menghindari blocking
                
            except requests.exceptions.RequestException as e:
                print(f"Error saat mengambil halaman {page}: {e}")
                break
            except Exception as e:
                print(f"Error lain saat mengambil halaman {page}: {e}")
                break
        
        return articles, total_pages
    
    def get_total_pages(self, soup):
        """Mendapatkan total halaman dari pagination"""
        try:
            # Cari pagination
            paging_div = soup.find('div', class_='paging__wrap')
            if paging_div:
                # Cari link "Last"
                last_link = paging_div.find('a', class_='paging__link--last')
                if last_link and 'page=' in last_link.get('href', ''):
                    match = re.search(r'page=(\d+)', last_link['href'])
                    if match:
                        return int(match.group(1))
                
                # Cari nomor halaman terbesar dari semua link
                page_links = paging_div.find_all('a', class_='paging__link')
                max_page = 1
                for link in page_links:
                    href = link.get('href', '')
                    if 'page=' in href:
                        match = re.search(r'page=(\d+)', href)
                        if match:
                            page_num = int(match.group(1))
                            if page_num > max_page:
                                max_page = page_num
                return max_page
            
            return 1
        except Exception as e:
            print(f"Tidak bisa mendapatkan total halaman: {e}")
            return 1
    
    def extract_search_result(self, article_item):
        """Ekstrak data dari hasil pencarian"""
        try:
            # Link artikel
            link_tag = article_item.find('a', class_='article-link')
            if not link_tag or 'href' not in link_tag.attrs:
                return None
            
            article_url = link_tag.get('href')
            if not article_url or article_url.startswith('javascript'):
                return None
            
            # Judul
            title_tag = article_item.find('h2', class_='articleTitle')
            title = title_tag.get_text(strip=True) if title_tag else ""
            
            # Gambar
            img_tag = article_item.find('img')
            image_url = img_tag.get('src') if img_tag and img_tag.get('src') else ""
            
            # Tanggal
            date_tag = article_item.find('div', class_='articlePost-date')
            date = date_tag.get_text(strip=True) if date_tag else ""
            
            # Kategori/tag
            category_tag = article_item.find('div', class_='articlePost-subtitle')
            category = category_tag.get_text(strip=True) if category_tag else ""
            
            # Ringkasan
            summary_tag = article_item.find('div', class_='articleLead')
            summary = summary_tag.get_text(strip=True) if summary_tag else ""
            
            return {
                'title': title,
                'url': article_url,
                'image_url': image_url,
                'date': date,
                'category': category,
                'summary': summary
            }
            
        except Exception as e:
            print(f"Error ekstrak hasil: {e}")
            return None
    
    def get_article_detail(self, url):
        """Ambil detail lengkap artikel"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print(f"   Mengambil detail: {url}")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Judul artikel
                title = self.extract_title(soup)
                
                # Penulis
                author = self.extract_author(soup)
                
                # Editor
                editor = self.extract_editor(soup)
                
                # Tanggal publish
                date_published = self.extract_date(soup, url)
                
                # Breadcrumb untuk kategori
                categories = self.extract_categories(soup)
                
                # Konten artikel
                content = self.extract_content(soup)
                
                # Tags
                tags = self.extract_tags(soup)
                
                # Halaman (untuk multi-page articles)
                pages = self.extract_pages(soup, url)
                
                article_data = {
                    'title': title,
                    'author': author,
                    'editor': editor,
                    'date_published': date_published,
                    'categories': ', '.join(categories),
                    'content': content,
                    'tags': ', '.join(tags),
                    'url': url,
                    'total_pages': len(pages)
                }
                
                # Karena sudah pakai ?page=all, tidak perlu ambil halaman tambahan
                article_data['multi_page'] = False
                
                return article_data
                
            except requests.exceptions.Timeout as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count  # Exponential backoff: 2, 4 seconds
                    print(f"   Timeout - Retry {retry_count}/{max_retries} dalam {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"   Error timeout setelah {max_retries} percobaan: {e}")
                    return None
                    
            except requests.exceptions.ConnectionError as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    print(f"   Connection error - Retry {retry_count}/{max_retries} dalam {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"   Error koneksi setelah {max_retries} percobaan: {e}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"   Error request: {e}")
                return None
                
            except Exception as e:
                print(f"   Error lain saat mengambil detail: {e}")
                return None
    
    def extract_title(self, soup):
        """Ekstrak judul artikel"""
        # Coba beberapa kemungkinan class untuk judul
        title_selectors = [
            'h1.read__title',
            'h1.article__title',
            'h1.post__title',
            'h1.title',
            'h1'
        ]
        
        for selector in title_selectors:
            title_tag = soup.select_one(selector)
            if title_tag:
                return title_tag.get_text(strip=True)
        
        # Coba dari meta tag
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            return meta_title['content']
        
        return ""
    
    def extract_author(self, soup):
        """Ekstrak penulis artikel"""
        # Coba beberapa selector untuk penulis
        author_selectors = [
            'div.opinion__author a.opinion__link',
            'div.read__credit a',
            'div.author a',
            'div.writer a',
            'span.author',
            'span.writer',
            'meta[name="author"]',
            'meta[property="article:author"]'
        ]
        
        for selector in author_selectors:
            if selector.startswith('meta'):
                meta = soup.select_one(selector)
                if meta and meta.get('content'):
                    return meta['content']
            else:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text and len(text) > 2:
                        return text
        
        return ""
    
    def extract_editor(self, soup):
        """Ekstrak editor"""
        # Cari di credit
        credit_div = soup.find('div', class_='read__credit')
        if credit_div:
            spans = credit_div.find_all('span')
            for span in spans:
                if 'Editor' in span.text:
                    next_a = span.find_next('a')
                    if next_a:
                        return next_a.get_text(strip=True)
        return ""
    
    def extract_date(self, soup, url=""):
        """Ekstrak tanggal publish"""
        # Coba dari URL (format: /read/YYYY/MM/DD/)
        date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
        if date_match:
            return f"{date_match.group(3)}-{date_match.group(2)}-{date_match.group(1)}"
        
        # Coba dari meta tag
        meta_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publishdate"]',
            'meta[name="date"]'
        ]
        
        for selector in meta_selectors:
            meta = soup.select_one(selector)
            if meta and meta.get('content'):
                date_str = meta['content']
                # Ekstrak hanya tanggal (YYYY-MM-DD)
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
                if date_match:
                    return date_match.group(1)
        
        return ""
    
    def extract_categories(self, soup):
        """Ekstrak kategori dari breadcrumb"""
        categories = []
        
        # Coba breadcrumb
        breadcrumb = soup.find('ul', class_='breadcrumb__wrap')
        if breadcrumb:
            items = breadcrumb.find_all('li', class_='breadcrumb__item')[1:]  # Skip home
            for item in items:
                link = item.find('a', class_='breadcrumb__link')
                if link:
                    text = link.get_text(strip=True)
                    if text and text.lower() != 'home' and 'kompas' not in text.lower():
                        categories.append(text)
        
        return categories
    
    def extract_content(self, soup):
        """Ekstrak konten artikel lengkap - SEMUA paragraf tanpa filter yang ketat"""
        # Coba beberapa selector untuk konten
        content_selectors = [
            'div.read__content',
            'div.article__content',
            'div.post__content',
            'div.content',
            'article'
        ]
        
        content_div = None
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                break
        
        if not content_div:
            return ""
        
        # Clone untuk menghindari modifikasi original
        import copy
        content_div_copy = copy.copy(content_div)
        
        # Hapus elemen yang PASTI bukan konten
        remove_selectors = [
            'script', 'style', 'iframe', 'noscript',
            'div.ads-on-body', 'div.ads-partner-wrap', 'div.kompasidRec',
            '[class*="ads-"]', '[class*="iklan"]', '[class*="recommend"]',
            '[class*="related"]', '[class*="komentar"]', '[class*="comment"]',
            '[class*="share"]', '[class*="sidebar"]', '[class*="video"]',
            'div.read__credit', 'div.tagsCloud-tag', 'div.wSpec', 'div.native-wrap',
            'div.fb-quote', '[id*="ads"]', '[id*="iklan"]',
            'span.ads-on-body', '[class*="DFP"]', 'span.liftdown_v2_tanda'
        ]
        
        for selector in remove_selectors:
            try:
                for element in content_div_copy.select(selector):
                    element.decompose()
            except:
                pass
        
        # Ambil SEMUA paragraf tanpa batasan
        paragraphs = content_div_copy.find_all('p', recursive=True)
        content_parts = []
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            
            # Hanya skip paragraf yang jelas iklan atau non-konten
            skip_keywords = [
                'berikan apresiasi',
                'dalam segala situasi, kompas.com berkomitmen',
                'kirimkan apresiasi spesial',
            ]
            
            # Ambil jika ada teks dan bukan keyword skip
            if text and len(text) > 0:
                should_skip = False
                for keyword in skip_keywords:
                    if keyword.lower() in text.lower():
                        should_skip = True
                        break
                
                # Jika paragraf dimulai dengan "Baca juga:" tapi ada lebih dari 30 karakter, ambil saja
                if text.lower().startswith('baca juga:') and len(text) > 30:
                    should_skip = True
                
                if not should_skip:
                    content_parts.append(text)
        
        # Jika masih kosong, coba ambil dengan cara lain
        if not content_parts:
            try:
                all_text = content_div_copy.get_text(separator='\n')
                lines = [line.strip() for line in all_text.split('\n') if line.strip() and len(line.strip()) > 10]
                content_parts = lines
            except:
                pass
        
        # Gabungkan semua paragraf
        if content_parts:
            full_content = "\n\n".join(content_parts)
            # Bersihkan whitespace berlebih
            full_content = '\n\n'.join([line for line in full_content.split('\n\n') if line.strip()])
            return full_content
        
        return ""
    
    def extract_tags(self, soup):
        """Ekstrak tags artikel"""
        tags = []
        
        # Coba dari tags section
        tags_section = soup.find('div', class_='tagsCloud-tag')
        if tags_section:
            tag_links = tags_section.find_all('a')
            for link in tag_links:
                tag_text = link.get_text(strip=True)
                if tag_text:
                    tags.append(tag_text)
        
        # Coba dari meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords = meta_keywords['content'].split(',')
            tags.extend([k.strip() for k in keywords if k.strip()])
        
        return list(set(tags))  # Hapus duplikat
    
    def extract_pages(self, soup, base_url):
        """Ekstrak link ke halaman lain - gunakan ?page=all untuk semuanya"""
        # Karena sudah menggunakan ?page=all, cukup return base_url saja
        # ?page=all sudah mengambil semua konten dalam satu halaman
        return [base_url]
    
    def get_page_content(self, url):
        """Ambil konten lengkap dari halaman tertentu - SEMUA paragraf"""
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            content_div = soup.find('div', class_='read__content')
            if not content_div:
                return ""
            
            # Clone untuk menghindari modifikasi original
            import copy
            content_div_copy = copy.copy(content_div)
            
            # Hapus elemen yang PASTI bukan konten
            remove_selectors = [
                'script', 'style', 'iframe', 'noscript',
                'div.ads-on-body', 'div.ads-partner-wrap', 'div.kompasidRec',
                '[class*="ads-"]', '[class*="iklan"]', '[class*="recommend"]',
                '[class*="related"]', '[class*="komentar"]', '[class*="comment"]',
                '[class*="share"]', '[class*="sidebar"]', '[class*="video"]',
                'div.read__credit', 'div.tagsCloud-tag', 'div.wSpec', 'div.native-wrap',
                'div.fb-quote', '[id*="ads"]', '[id*="iklan"]',
                'span.ads-on-body', '[class*="DFP"]', 'span.liftdown_v2_tanda'
            ]
            
            for selector in remove_selectors:
                try:
                    for element in content_div_copy.select(selector):
                        element.decompose()
                except:
                    pass
            
            # Ambil SEMUA paragraf
            paragraphs = content_div_copy.find_all('p', recursive=True)
            content_parts = []
            
            for p in paragraphs:
                text = p.get_text(strip=True)
                
                # Hanya skip paragraf yang jelas iklan
                skip_keywords = [
                    'berikan apresiasi',
                    'dalam segala situasi, kompas.com berkomitmen',
                    'kirimkan apresiasi spesial',
                ]
                
                if text and len(text) > 0:
                    should_skip = False
                    for keyword in skip_keywords:
                        if keyword.lower() in text.lower():
                            should_skip = True
                            break
                    
                    if not should_skip:
                        content_parts.append(text)
            
            return "\n\n".join(content_parts)
            
        except Exception as e:
            print(f"   Error mengambil halaman: {e}")
            return ""
    
    def scrape_by_keyword(self, keyword, max_search_pages=None, max_articles=None):
        """
        Scraping lengkap berdasarkan keyword
        
        Args:
            keyword: Kata kunci pencarian
            max_search_pages: Maksimal halaman pencarian (default: None = semua)
            max_articles: Maksimal artikel yang diambil (default: None = semua)
            
        Returns:
            List of article data
        """
        print(f"\n{'='*60}")
        print(f"MEMULAI SCRAPING KOMPAS")
        print(f"Keyword: {keyword}")
        print(f"{'='*60}")
        
        # Cari artikel
        articles, total_pages = self.search_articles(keyword, max_pages=max_search_pages)
        
        if not articles:
            print("Tidak ada artikel yang ditemukan!")
            return []
        
        print(f"\nHASIL PENCARIAN:")
        print(f"   Total artikel ditemukan: {len(articles)}")
        print(f"   Total halaman tersedia: {total_pages}")
        
        # Jika max_articles tidak ditentukan, ambil semua
        if max_articles is None:
            max_articles = len(articles)
        
        # Batasi jumlah artikel
        articles = articles[:max_articles]
        
        print(f"\nMENGAMBIL DETAIL {len(articles)} ARTIKEL...")
        print(f"{'='*60}")
        
        results = []
        success_count = 0
        
        for i, article in enumerate(articles, 1):
            print(f"\n[{i}/{len(articles)}] Memproses: {article['title'][:60]}...")
            
            # Ambil detail lengkap
            detail = self.get_article_detail(article['url'])
            
            if detail:
                # Gabungkan dengan data pencarian
                article.update(detail)
                results.append(article)
                success_count += 1
                print(f"   Berhasil diambil ({len(detail['content'])} karakter)")
            else:
                # Simpan data dasar saja
                article['content'] = "Gagal mengambil konten"
                article['author'] = ""
                article['date_published'] = article['date']
                article['categories'] = article['category']
                article['tags'] = ""
                article['total_pages'] = 1
                article['multi_page'] = False
                results.append(article)
                print(f"   Gagal mengambil detail, menyimpan data dasar")
            
            # Delay untuk menghindari blocking
            if i < len(articles):
                time.sleep(2)
        
        print(f"\n{'='*60}")
        print(f"SCRAPING SELESAI!")
        print(f"Hasil: {success_count}/{len(articles)} artikel berhasil diambil detailnya")
        print(f"{'='*60}")
        
        return results
    
    def save_to_excel(self, data, filename):
        """Simpan hasil ke file Excel"""
        if not data:
            print("Tidak ada data untuk disimpan!")
            return
        
        # Buat direktori jika belum ada
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Siapkan data untuk DataFrame
        excel_data = []
        for article in data:
            row = {
                'No': len(excel_data) + 1,
                'Judul': article.get('title', ''),
                'Tanggal': article.get('date_published', article.get('date', '')),
                'Penulis': article.get('author', ''),
                'Editor': article.get('editor', ''),
                'Kategori': article.get('categories', article.get('category', '')),
                'Tags': article.get('tags', ''),
                'Ringkasan': article.get('summary', ''),
                'Konten': article.get('content', ''),
                'URL': article.get('url', ''),
                'Gambar': article.get('image_url', ''),
                'Jumlah Halaman': article.get('total_pages', 1),
                'Multi Halaman': 'Ya' if article.get('multi_page', False) else 'Tidak'
            }
            excel_data.append(row)
        
        # Buat DataFrame
        df = pd.DataFrame(excel_data)
        
        # Simpan ke Excel
        try:
            # Gunakan xlsxwriter untuk format yang lebih baik
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Kompas Artikel', index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Kompas Artikel']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            print(f"Data disimpan ke Excel: {filename}")
            print(f"   Total baris: {len(df)}")
            print(f"   Total kolom: {len(df.columns)}")
            
        except Exception as e:
            print(f"Error menyimpan ke Excel: {e}")
            # Fallback ke CSV
            csv_file = filename.replace('.xlsx', '.csv')
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"Data disimpan ke CSV: {csv_file}")
    
    def save_to_json(self, data, filename):
        """Simpan hasil ke file JSON"""
        # Buat direktori jika belum ada
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data disimpan ke JSON: {filename}")
    
    def save_to_txt(self, data, filename):
        """Simpan hasil ke file teks"""
        # Buat direktori jika belum ada
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"{'='*60}\n")
            f.write(f"LAPORAN SCRAPING KOMPAS\n")
            f.write(f"{'='*60}\n\n")
            
            for i, article in enumerate(data, 1):
                f.write(f"{'='*60}\n")
                f.write(f"ARTIKEL {i}\n")
                f.write(f"{'='*60}\n\n")
                
                f.write(f"JUDUL: {article.get('title', 'N/A')}\n")
                f.write(f"TANGGAL: {article.get('date_published', article.get('date', 'N/A'))}\n")
                f.write(f"PENULIS: {article.get('author', 'N/A')}\n")
                f.write(f"EDITOR: {article.get('editor', 'N/A')}\n")
                f.write(f"KATEGORI: {article.get('categories', article.get('category', 'N/A'))}\n")
                f.write(f"TAGS: {article.get('tags', 'N/A')}\n")
                f.write(f"URL: {article.get('url', 'N/A')}\n")
                f.write(f"GAMBAR: {article.get('image_url', 'N/A')}\n")
                f.write(f"JML HALAMAN: {article.get('total_pages', 1)}\n")
                f.write(f"MULTI HALAMAN: {'Ya' if article.get('multi_page', False) else 'Tidak'}\n\n")
                
                f.write(f"RINGKASAN:\n{article.get('summary', 'N/A')}\n\n")
                
                f.write(f"KONTEN LENGKAP:\n")
                content = article.get('content', 'N/A')
                if content and content != "Gagal mengambil konten":
                    f.write(f"{content}\n")
                else:
                    f.write(f"{content}\n")
                
                f.write(f"\n{'-'*50}\n\n")
        
        print(f"Data disimpan ke TXT: {filename}")
