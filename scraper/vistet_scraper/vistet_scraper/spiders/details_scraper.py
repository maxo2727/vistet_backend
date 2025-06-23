import json
import re
from urllib.parse import urljoin

import requests
import scrapy
import vistet_scraper.items as items


class DetailsSpider(scrapy.Spider):
    name = "details_spider"
    start_urls = ["https://www.vistet.com/products/1234567890"]

    api_base_url = "http://localhost:8000/api/"

    def start_requests(self):
        url = "https://rehabclo.cl/collections/productos"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Extract product data and save to database"""

        products_data = self.extract_products_from_js(response)

        if products_data:
            print(f"✅ Found {len(products_data)} products")

            saved_count = self.save_products_to_database(products_data)
            print(f"✅ Successfully saved {saved_count} products to database")
        else:
            print("❌ No product data found")

    def extract_products_from_js(self, response):
        """Extract product data from JavaScript variables"""
        html = response.text
        products = []

        # Extract products from ShopifyAnalytics.meta section
        meta_products = self.extract_meta_products(html)
        
        # Extract images from web pixels manager script section
        image_mapping = self.extract_images_from_web_pixels(html)
        
        print(f"📦 Meta products found: {len(meta_products)}")
        print(f"🖼️ Image mappings found: {len(image_mapping)}")

        # Process each product and match with images
        for product in meta_products:
            processed_product = self.process_product_data(product, image_mapping)
            if processed_product:
                products.append(processed_product)

        return products

    def extract_meta_products(self, html):
        """Extract product data from ShopifyAnalytics.meta section"""
        meta_pattern = r'var meta = ({.*?"products":\[.*?\].*?});'
        meta_match = re.search(meta_pattern, html, re.DOTALL)

        if meta_match:
            try:
                meta_data = json.loads(meta_match.group(1))
                return meta_data.get("products", [])
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing meta JSON: {e}")
                return []
        
        return []

    def extract_images_from_web_pixels(self, html):
        """Extract image URLs from web pixels manager section"""
        image_mapping = {}
        
        # Look for the collection_viewed event with productVariants
        web_pixels_pattern = r'webPixelsManagerAPI\.publish\("collection_viewed",\s*({.*?"productVariants":\[.*?\].*?})\)'
        web_pixels_match = re.search(web_pixels_pattern, html, re.DOTALL)
        
        if web_pixels_match:
            try:
                collection_data = json.loads(web_pixels_match.group(1))
                product_variants = collection_data.get("collection", {}).get("productVariants", [])
                
                print(f"🔍 Found {len(product_variants)} product variants with images")
                
                # Create mapping from product ID to image URL
                for variant in product_variants:
                    product_info = variant.get("product", {})
                    product_id = product_info.get("id")
                    image_info = variant.get("image", {})
                    image_src = image_info.get("src", "")
                    
                    if product_id and image_src:
                        if image_src.startswith("//"):
                            image_url = "https:" + image_src
                        elif image_src.startswith("/"):
                            image_url = "https://rehabclo.cl" + image_src
                        elif not image_src.startswith("http"):
                            image_url = "https://rehabclo.cl/" + image_src.lstrip("/")
                        else:
                            image_url = image_src
                            
                        try:
                            from urllib.parse import urlparse
                            parsed = urlparse(image_url)
                            if parsed.scheme and parsed.netloc:
                                image_mapping[int(product_id)] = image_url
                                print(f"🖼️ Mapped product {product_id} to image: {image_url}")
                            else:
                                print(f"⚠️ Invalid URL for product {product_id}: {image_url}")
                        except Exception as e:
                            print(f"❌ Error parsing URL for product {product_id}: {e}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing web pixels JSON: {e}")
        else:
            print("⚠️ Web pixels collection_viewed section not found")
        
        return image_mapping

    def process_product_data(self, raw_product, image_mapping):
        """Process raw product data into API format with correct image URL"""
        try:
            product_id = raw_product.get("id")
            
            product_data = {
                "id": product_id,
                "gid": raw_product.get("gid", ""),
                "vendor": raw_product.get("vendor", ""),
                "type": raw_product.get("type", ""),
                "title": self.extract_product_name(raw_product),
                "variants": raw_product.get("variants", []),
                "image_url": image_mapping.get(product_id, ""),
            }

            if not product_data["id"] or not product_data["title"]:
                print(f"⚠️ Skipping product with missing ID or title: {product_data}")
                return None

            if product_data["image_url"] and product_data["image_url"] != "":
                print(f"📝 Processed: {product_data['title']} ({product_data['type']}) - Image: ✅")
            else:
                print(f"📝 Processed: {product_data['title']} ({product_data['type']}) - Image: ❌")
                
            return product_data

        except Exception as e:
            print(f"❌ Error processing product: {e}")
            return None

    def extract_product_name(self, product):
        """Extract product name from various possible fields"""
        for field in ["title", "name", "product_title"]:
            if product.get(field):
                return product[field]

        if product.get("variants") and len(product["variants"]) > 0:
            first_variant = product["variants"][0]
            variant_name = first_variant.get("name", "")
            if variant_name and " - " in variant_name:
                return variant_name.split(" - ")[0]

        return f"Product {product.get('id', 'Unknown')}"

    def save_products_to_database(self, products_data):
        """Save products to database via API"""
        saved_count = 0

        for product_data in products_data:
            try:
                print(f"🔗 Sending image URL for {product_data.get('title', 'Unknown')}: {product_data.get('image_url', 'No URL')}")
                
                api_url = urljoin(self.api_base_url, "clothe/from-scraped/")

                response = requests.post(
                    api_url,
                    json=product_data,
                    headers={
                        "Content-Type": "application/json",
                    },
                    timeout=10,
                )

                if response.status_code in [200, 201]:
                    saved_count += 1
                    result = response.json()
                    print(
                        f"✅ Saved: {result.get('name', 'Unknown')} (ID: {result.get('id', 'Unknown')})"
                    )
                else:
                    print(
                        f"❌ Failed to save {product_data.get('title', 'Unknown')}: {response.status_code}"
                    )
                    print(f"   Response: {response.text}")

            except requests.RequestException as e:
                print(
                    f"❌ Network error saving {product_data.get('title', 'Unknown')}: {e}"
                )
            except Exception as e:
                print(f"❌ Error saving {product_data.get('title', 'Unknown')}: {e}")

        return saved_count

    def save_products_bulk(self, products_data):
        """Save all products in one bulk request"""
        try:
            api_url = urljoin(self.api_base_url, "clothe/bulk-from-scraped/")

            payload = {"products": products_data}

            response = requests.post(
                api_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                },
                timeout=30,
            )

            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Bulk save successful: {result.get('message', '')}")
                return result.get("created", 0) + result.get("updated", 0)
            else:
                print(f"❌ Bulk save failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return 0

        except Exception as e:
            print(f"❌ Bulk save error: {e}")
            return 0
