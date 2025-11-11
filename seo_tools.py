
#!/usr/bin/env python3
"""
SEO Tools untuk Hurtrock Music Store
Tools untuk membantu optimasi SEO dan submit ke Google Search Console
"""

import requests
import json
from datetime import datetime, timedelta
from urllib.parse import urljoin
from main import app, models, db

def generate_url_list():
    """Generate list of all URLs for Google Search Console submission"""
    with app.app_context():
        urls = []
        base_url = "https://hurtrock-store.com"  # Ganti dengan domain real Anda
        
        # Homepage
        urls.append(base_url)
        
        # Product pages
        products = models.Product.query.filter_by(is_active=True).all()
        for product in products:
            if product.slug:
                urls.append(f"{base_url}/produk/{product.slug}")
        
        # Category pages
        categories = models.Category.query.filter_by(is_active=True).all()
        for category in categories:
            urls.append(f"{base_url}/products?category={category.id}")
        
        # Other important pages
        urls.extend([
            f"{base_url}/products",
            f"{base_url}/store-info",
        ])
        
        return urls

def check_page_indexing(url):
    """Check if page is indexed in Google (simple check)"""
    search_query = f"site:{url}"
    # Note: Google doesn't allow automated searches, ini hanya contoh
    # Gunakan Google Search Console API yang official untuk real implementation
    print(f"Check indexing for: {url}")
    print(f"Google search: {search_query}")
    return True

def generate_google_search_console_commands():
    """Generate commands for Google Search Console"""
    urls = generate_url_list()
    
    print("=== PANDUAN GOOGLE SEARCH CONSOLE ===")
    print("\n1. Buka Google Search Console: https://search.google.com/search-console/")
    print("2. Tambahkan property untuk domain: hurtrock-store.com")
    print("3. Verifikasi kepemilikan domain")
    print("\n4. Submit Sitemap:")
    print("   - Pergi ke Sitemaps")
    print("   - Submit: https://hurtrock-store.com/sitemap.xml")
    
    print("\n5. URL Inspection untuk halaman penting:")
    for i, url in enumerate(urls[:10]):  # First 10 URLs
        print(f"   - {url}")
    
    print("\n6. Request Indexing untuk halaman baru:")
    print("   - Gunakan URL Inspection tool")
    print("   - Paste URL yang ingin diindex")
    print("   - Klik 'Request Indexing'")
    
    print(f"\nTotal URLs to monitor: {len(urls)}")

def validate_seo_setup():
    """Validate SEO setup"""
    with app.app_context():
        print("=== VALIDASI SEO SETUP ===")
        
        # Check if products have slugs
        products_without_slug = models.Product.query.filter_by(slug=None, is_active=True).count()
        print(f"Products without slug: {products_without_slug}")
        
        # Check if products have descriptions
        products_without_desc = models.Product.query.filter_by(description=None, is_active=True).count()
        print(f"Products without description: {products_without_desc}")
        
        # Check total active products
        total_products = models.Product.query.filter_by(is_active=True).count()
        print(f"Total active products: {total_products}")
        
        # Check categories
        total_categories = models.Category.query.filter_by(is_active=True).count()
        print(f"Total active categories: {total_categories}")
        
        print("\n=== REKOMENDASI ===")
        if products_without_slug > 0:
            print("- Jalankan script untuk generate slug untuk semua produk")
        if products_without_desc > 0:
            print("- Tambahkan deskripsi untuk produk yang belum ada")
        print("- Submit sitemap.xml ke Google Search Console")
        print("- Monitor indexing status secara berkala")
        print("- Tambahkan internal linking antar halaman produk")

if __name__ == "__main__":
    print("SEO Tools untuk Hurtrock Music Store")
    print("=" * 50)
    
    validate_seo_setup()
    print()
    generate_google_search_console_commands()
    
    # Generate URL list file
    urls = generate_url_list()
    with open("urls_for_google.txt", "w") as f:
        for url in urls:
            f.write(url + "\n")
    
    print(f"\nURL list saved to: urls_for_google.txt")
