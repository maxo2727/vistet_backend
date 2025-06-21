import scrapy
import vistet_scraper.items as items
import json
import re

class DetailsSpider(scrapy.Spider):
  name = "details_spider"
  start_urls = ["https://www.vistet.com/products/1234567890"]

  def start_requests(self): 
    url = "https://rehabclo.cl/collections/productos"
    yield scrapy.Request(url=url, callback=self.parse)

  def parse(self, response):
    item = items.VistetScraperItem()
    
    # Extract web-pixels-manager-setup script
    web_pixels_script = response.css('script#web-pixels-manager-setup::text').get()
    if web_pixels_script:
      print("✅ Found web-pixels-manager-setup script:")
      print("=" * 50)
      print(web_pixels_script)
      print("=" * 50)
    else:
      print("❌ web-pixels-manager-setup script not found")
    
    # Extract ShopifyAnalytics script
    shopify_analytics_scripts = response.css('script:contains("ShopifyAnalytics")::text').getall()
    if shopify_analytics_scripts:
      print("✅ Found ShopifyAnalytics script(s):")
      for i, script in enumerate(shopify_analytics_scripts):
        print(f"=" * 30 + f" Script {i+1} " + "=" * 30)
        print(script.strip())
        print("=" * 70)
    else:
      print("❌ ShopifyAnalytics scripts not found")
    
    # Alternative: Search for any script containing product data
    all_scripts = response.css('script::text').getall()
    product_scripts = []
    
    for script in all_scripts:
      if 'products' in script and ('meta' in script or 'ShopifyAnalytics' in script):
        product_scripts.append(script)
    
    if product_scripts:
      print("✅ Found scripts with product data:")
      for i, script in enumerate(product_scripts):
        print(f"=" * 25 + f" Product Script {i+1} " + "=" * 25)
        print(script.strip())
        print("=" * 60)
    
    # Try to extract specific data using regex
    self.extract_product_data(response)
    
  def extract_product_data(self, response):
    """Extract product data from JavaScript variables"""
    html = response.text
    
    # Look for the ShopifyAnalytics.meta pattern
    meta_pattern = r'window\.ShopifyAnalytics\.meta\s*=\s*(.*?);'
    meta_match = re.search(meta_pattern, html, re.DOTALL)
    
    if meta_match:
      print("✅ Found ShopifyAnalytics.meta data:")
      print("=" * 40)
      print(meta_match.group(1))
      print("=" * 40)
    
    # Look for the products array specifically
    products_pattern = r'var meta = (.*?);'
    products_match = re.search(products_pattern, html, re.DOTALL)
    
    if products_match:
      print("✅ Found meta variable with products:")
      print("=" * 40)
      try:
        # Try to parse as JSON
        meta_data = products_match.group(1)
        print(meta_data)
      except:
        print("Raw data:")
        print(products_match.group(1))
      print("=" * 40)