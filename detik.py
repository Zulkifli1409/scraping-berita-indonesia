import requests
from bs4 import BeautifulSoup
import time
import json
import pandas as pd
from datetime import datetime
import re

class DetikScraper:
    def __init__(self):
        self.base_url = "https://www.detik.com"
        self.search_url = f"{self.base_url}/search/searchall"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    def get_total_search_pages(self, keyword):
        """Mendapatkan total halaman hasil pencarian"""
        print(f"[SEARCHING] Mengecek total halaman untuk keyword: {keyword}")
        
        params = {
            'query': keyword,
            'result_type': 'relevansi'
        }
        
        try:
            response = requests.get(self.search_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Cari pagination
            pagination = soup.find('div', class_='pagination')
            if pagination:
                # Ambil semua link pagination
                page_links = pagination.find_all('a', class_='pagination__item')
                
                # Cari halaman terakhir (yang bukan "Next" atau "Prev")
                max_page = 1
                for link in page_links:
                    text = link.get_text(strip=True)
                    if text.isdigit():
                        page_num = int(text)
                        if page_num > max_page:
                            max_page = page_num
                
                print(f"Total halaman ditemukan: {max_page}")
                return max_page
            else:
                print("Pagination tidak ditemukan, return 1 halaman")
                return 1
                
        except Exception as e:
            print(f"Error saat mengecek total halaman: {str(e)}")
            return 1
    
    def search_articles(self, keyword, max_pages=5):
        """Mencari artikel berdasarkan keyword"""
        print(f"[SEARCHING] Memulai pencarian untuk keyword: {keyword}")
        
        all_articles = []
        
        for page in range(1, max_pages + 1):
            print(f"Mengambil halaman {page}...")
            
            params = {
                'query': keyword,
                'result_type': 'relevansi',
                'page': page
            }
            
            try:
                response = requests.get(self.search_url, params=params, headers=self.headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Cari semua artikel
                articles = soup.find_all('article', class_='list-content__item')
                
                for article in articles:
                    try:
                        # Extract title dan URL
                        title_elem = article.find('h3', class_='media__title')
                        if not title_elem:
                            continue
                        
                        link_elem = title_elem.find('a', class_='media__link')
                        if not link_elem:
                            continue
                        
                        title = link_elem.get_text(strip=True)
                        url = link_elem.get('href', '')
                        
                        # Extract category
                        category_elem = article.find('h2', class_='media__subtitle')
                        category = category_elem.get_text(strip=True) if category_elem else ''
                        
                        # Extract date
                        date_elem = article.find('div', class_='media__date')
                        date_text = ''
                        if date_elem:
                            date_span = date_elem.find('span')
                            if date_span:
                                date_text = date_span.get_text(strip=True)
                        
                        # Extract description
                        desc_elem = article.find('div', class_='media__desc')
                        description = desc_elem.get_text(strip=True) if desc_elem else ''
                        
                        article_data = {
                            'title': title,
                            'url': url,
                            'category': category,
                            'date': date_text,
                            'description': description
                        }
                        
                        all_articles.append(article_data)
                        
                    except Exception as e:
                        print(f"Error parsing artikel: {str(e)}")
                        continue
                
                print(f"Ditemukan {len(articles)} artikel di halaman {page}")
                
                # Delay untuk menghindari rate limit
                if page < max_pages:
                    time.sleep(1)
                    
            except Exception as e:
                print(f"Error saat mengambil halaman {page}: {str(e)}")
                continue
        
        print(f"Total artikel ditemukan: {len(all_articles)}")
        return all_articles, max_pages
    
    def get_article_detail(self, url):
        """Mengambil detail lengkap artikel"""
        print(f"   Mengambil detail: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1', class_='detail__title')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Extract author (bisa dari box-kolumnis atau byline lain)
            author = ''
            # Cek kolumnis box
            author_elem = soup.find('div', class_='box-kolumnis__desc')
            if author_elem:
                author_name = author_elem.find('h5')
                if author_name:
                    author = author_name.get_text(strip=True)
            
            # Jika tidak ada, cek struktur lain
            if not author:
                byline = soup.find('div', class_='detail__author')
                if byline:
                    author = byline.get_text(strip=True)
            
            # Extract date
            date_elem = soup.find('div', class_='detail__date')
            date_published = date_elem.get_text(strip=True) if date_elem else ''
            
            # Extract content
            content_elem = soup.find('div', class_='detail__body-text')
            if content_elem:
                # Remove script dan style tags
                for script in content_elem(['script', 'style', 'ins', 'div']):
                    script.decompose()
                
                # Ambil semua paragraf
                paragraphs = content_elem.find_all(['p', 'strong'])
                content = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            else:
                content = ''
            
            # Extract tags
            tags = []
            tag_container = soup.find('div', class_='detail__body-tag')
            if tag_container:
                tag_links = tag_container.find_all('a', class_='nav__item')
                tags = [tag.get_text(strip=True) for tag in tag_links]
            
            # Extract category
            category_elem = soup.find('h2', class_='detail__subtitle')
            category = category_elem.get_text(strip=True) if category_elem else ''
            
            return {
                'title': title,
                'author': author,
                'date_published': date_published,
                'content': content,
                'categories': category,
                'tags': ', '.join(tags),
                'total_pages': 1,
                'multi_page': False
            }
            
        except Exception as e:
            print(f"   Error mengambil detail artikel: {str(e)}")
            return None
    
    def save_to_excel(self, articles, filename):
        """Menyimpan data ke Excel"""
        df = pd.DataFrame(articles)
        
        # Reorder columns
        columns_order = ['title', 'url', 'category', 'date', 'date_published', 
                        'author', 'description', 'content', 'categories', 'tags']
        
        # Only include columns that exist
        columns_order = [col for col in columns_order if col in df.columns]
        df = df[columns_order]
        
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Data disimpan ke Excel: {filename}")
        
    def save_to_json(self, articles, filename):
        """Menyimpan data ke JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"Data disimpan ke JSON: {filename}")
        
    def save_to_txt(self, articles, filename):
        """Menyimpan data ke TXT"""
        with open(filename, 'w', encoding='utf-8') as f:
            for i, article in enumerate(articles, 1):
                f.write(f"{'='*80}\n")
                f.write(f"ARTIKEL {i}\n")
                f.write(f"{'='*80}\n\n")
                f.write(f"Judul: {article.get('title', '')}\n")
                f.write(f"URL: {article.get('url', '')}\n")
                f.write(f"Kategori: {article.get('category', '')} - {article.get('categories', '')}\n")
                f.write(f"Tanggal: {article.get('date_published', article.get('date', ''))}\n")
                f.write(f"Penulis: {article.get('author', '')}\n")
                f.write(f"Tags: {article.get('tags', '')}\n\n")
                f.write(f"Deskripsi:\n{article.get('description', '')}\n\n")
                f.write(f"Konten:\n{article.get('content', '')}\n\n")
                f.write("\n\n")
        
        print(f"Data disimpan ke TXT: {filename}")
