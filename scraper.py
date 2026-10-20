import asyncio
import os
# 1. Update the imports
from playwright.async_api import async_playwright
from playwright_stealth import Stealth 
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def scrape_properties():
    # 2. Use the new Stealth().use_async() context manager wrapper
    async with Stealth().use_async(async_playwright()) as p:
        # Launch browser in headless mode
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # The stealth patches are now automatically applied to 'page'
        # No need to call stealth_async(page) anymore
        
        target_url = "https://www.nobroker.in/property/rent/bangalore/Banashankari?searchParam=W3sibGF0IjoxMi45MjU0NTMzLCJsb24iOjc3LjU0Njc1NywicGxhY2VJZCI6IkNoSUp0MWpESWl3LXJqc1I3X0kyZnhCb2NCVSIsInBsYWNlTmFtZSI6IkJhbmFzaGFua2FyaSJ9XQ==&radius=2.0&sharedAccomodation=0&city=bangalore&locality=Banashankari"
        print(f"Navigating to {target_url}...")
        await page.goto(target_url, wait_until="domcontentloaded")
        
        # Wait for the property cards to load on the screen
        await page.wait_for_selector(".property-card-class") 
        
        scraped_data = []
        cards = await page.query_selector_all(".property-card-class")
        
        for card in cards:
            # Extract relevant text (You will need to inspect the actual website's DOM for exact class names)
            price_text = await card.query_selector(".price-class")
            area_text = await card.query_selector(".carpet-area-class")
            floor_text = await card.query_selector(".floor-details-class")
            
            # Clean and format the data
            price = clean_price(await price_text.inner_text()) if price_text else 0
            carpet_area = clean_area(await area_text.inner_text()) if area_text else 0
            floor = await floor_text.inner_text() if floor_text else "Unknown"
            
            scraped_data.append({
                "source": "Portal_Name",
                "price": price,
                "carpet_area_sqft": carpet_area,
                "floor_range": floor,
                # Location would be passed here if parsing exact coordinates
            })
            
        print(f"Extracted {len(scraped_data)} properties. Pushing to Supabase...")
        
        # Insert batch into Supabase
        if scraped_data:
            supabase.table("listings").insert(scraped_data).execute()
            
        await browser.close()

# Helper functions to convert "₹2.5 Cr" to integers would go here
def clean_price(text):
    pass 
def clean_area(text):
    pass

if __name__ == "__main__":
    asyncio.run(scrape_properties())