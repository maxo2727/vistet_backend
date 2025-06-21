import scrapy
import vistet_scraper.items as items
import json
import re
import requests
from urllib.parse import urljoin

class DetailsSpider(scrapy.Spider):
    name = "details_spider"
    start_urls = ["https://www.vistet.com/products/1234567890"]
    
    # API base URL - adjust if your Django server runs on different port
    api_base_url = "http://localhost:8000/api/"

    def start_requests(self): 
        url = "https://rehabclo.cl/collections/productos"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Extract product data and save to database"""
        
        # Extract product data from JavaScript
        products_data = self.extract_products_from_js(response)
        
        if products_data:
            print(f"✅ Found {len(products_data)} products")
            
            # Save products to database via API
            saved_count = self.save_products_to_database(products_data)
            print(f"✅ Successfully saved {saved_count} products to database")
        else:
            print("❌ No product data found")
    
    def extract_products_from_js(self, response):
        """Extract product data from JavaScript variables"""
        html = response.text
        products = []
        
        # Look for the ShopifyAnalytics.meta pattern
        meta_pattern = r'var meta = ({.*?"products":\[.*?\].*?});'
        meta_match = re.search(meta_pattern, html, re.DOTALL)
        
        if meta_match:
            try:
                # Parse the meta JSON
                meta_data = json.loads(meta_match.group(1))
                products_raw = meta_data.get('products', [])
                
                print(f"📦 Raw products found: {len(products_raw)}")
                
                # Process each product
                for product in products_raw:
                    processed_product = self.process_product_data(product)
                    if processed_product:
                        products.append(processed_product)
                        
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing JSON: {e}")
                
        # Alternative: Look for web-pixels-manager data
        if not products:
            web_pixels_pattern = r'webPixelsConfigList.*?"collection_viewed".*?"productVariants":\[(.*?)\]'
            web_pixels_match = re.search(web_pixels_pattern, html, re.DOTALL)
            
            if web_pixels_match:
                print("🔍 Found web-pixels data, extracting...")
                # This is more complex parsing, you can extend this if needed
        
        return products
    
    def process_product_data(self, raw_product):
        """Process raw product data into API format"""
        try:
            # Extract basic product info
            product_data = {
                'id': raw_product.get('id'),
                'gid': raw_product.get('gid', ''),
                'vendor': raw_product.get('vendor', ''),
                'type': raw_product.get('type', ''),
                'title': self.extract_product_name(raw_product),
                'variants': raw_product.get('variants', []),
                'image_url': self.extract_product_image(raw_product)
            }
            
            # Validate required fields
            if not product_data['id'] or not product_data['title']:
                print(f"⚠️ Skipping product with missing ID or title: {product_data}")
                return None
            
            print(f"📝 Processed: {product_data['title']} ({product_data['type']})")
            return product_data
            
        except Exception as e:
            print(f"❌ Error processing product: {e}")
            return None
    
    def extract_product_name(self, product):
        """Extract product name from various possible fields"""
        # Try different possible name fields
        for field in ['title', 'name', 'product_title']:
            if product.get(field):
                return product[field]
        
        # If no direct name, try to construct from variants
        if product.get('variants') and len(product['variants']) > 0:
            first_variant = product['variants'][0]
            variant_name = first_variant.get('name', '')
            if variant_name and ' - ' in variant_name:
                return variant_name.split(' - ')[0]
        
        return f"Product {product.get('id', 'Unknown')}"
    
    def extract_product_image(self, product):
        """Extract product image URL"""
        # Try different possible image fields
        for field in ['image', 'image_url', 'featured_image']:
            if product.get(field):
                return product[field]
        
        # Try to get from variants
        if product.get('variants'):
            for variant in product['variants']:
                if variant.get('image'):
                    return variant['image'].get('src', '')
        
        return ''
    
    def save_products_to_database(self, products_data):
        """Save products to database via API"""
        saved_count = 0
        
        for product_data in products_data:
            try:
                # Send POST request to API
                api_url = urljoin(self.api_base_url, 'clothe/from-scraped/')
                
                response = requests.post(
                    api_url,
                    json=product_data,
                    headers={
                        'Content-Type': 'application/json',
                    },
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    saved_count += 1
                    result = response.json()
                    print(f"✅ Saved: {result.get('name', 'Unknown')} (ID: {result.get('id', 'Unknown')})")
                else:
                    print(f"❌ Failed to save {product_data.get('title', 'Unknown')}: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except requests.RequestException as e:
                print(f"❌ Network error saving {product_data.get('title', 'Unknown')}: {e}")
            except Exception as e:
                print(f"❌ Error saving {product_data.get('title', 'Unknown')}: {e}")
        
        return saved_count
    
    def save_products_bulk(self, products_data):
        """Alternative method: Save all products in one bulk request"""
        try:
            api_url = urljoin(self.api_base_url, 'clothe/bulk-from-scraped/')
            
            payload = {'products': products_data}
            
            response = requests.post(
                api_url,
                json=payload,
                headers={
                    'Content-Type': 'application/json',
                },
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Bulk save successful: {result.get('message', '')}")
                return result.get('created', 0) + result.get('updated', 0)
            else:
                print(f"❌ Bulk save failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return 0
                
        except Exception as e:
            print(f"❌ Bulk save error: {e}")
            return 0