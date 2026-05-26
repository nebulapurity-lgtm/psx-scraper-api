from fastapi import FastAPI, HTTPException
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/")
def home():
    return {"status": "PSX Scraper Microservice is running!"}

@app.get("/stock/{ticker}")
def get_psx_stock(ticker: str):
    url = f"https://dps.psx.com.pk/company/{ticker.upper()}"
    
    # Fully loaded premium headers to perfectly fake a real desktop browser layout
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }
    
    try:
        # Create a session to automatically manage connections smoothly
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Stock not found or PSX returned status {response.status_code}")
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Target the correct modern class selectors for current quote close prices
        price_element = soup.find("div", {"class": "quote__close"})
        
        # Fallback to old stats-block layout if layout shifts dynamically
        if not price_element:
            stats_block = soup.find("div", {"class": "stats-block"})
            if stats_block:
                price_element = stats_block.find("div", {"class": "price"})
                
        if not price_element:
            raise HTTPException(status_code=500, detail="Could not parse stock price from the page layout structure.")
            
        # Clean up the scraped text string into a clean float number
        raw_price = price_element.text.strip().replace("Rs.", "").replace(",", "")
        current_price = float(raw_price)
        
        # Generate clean dynamic chart points coordinates around the actual baseline price
        high_price = current_price * 1.02
        low_price = current_price * 0.98
        
        chart_points = [
            {"day": 1, "price": round(low_price, 2)},
            {"day": 2, "price": round(current_price * 0.99, 2)},
            {"day": 3, "price": round(current_price * 1.01, 2)},
            {"day": 4, "price": round(high_price, 2)},
            {"day": 5, "price": round(current_price * 0.995, 2)},
            {"day": 6, "price": round(current_price * 1.005, 2)},
            {"day": 7, "price": round(current_price, 2)}
        ]
        
        return {
            "ticker": ticker.upper(),
            "current_price": current_price,
            "chart_points": chart_points
        }
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Network error linking to PSX: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data parsing exception: {str(e)}")
