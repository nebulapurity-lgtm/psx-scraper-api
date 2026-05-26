from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Direct Yahoo Finance PSX API is running!"}

@app.get("/stock/{ticker}")
def get_psx_stock(ticker: str):
    yf_ticker = f"{ticker.upper()}.KA"
    # Querying the raw public market engine data stream directly
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yf_ticker}?range=7d&interval=1d"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker} not found on market stream.")
            
        data = response.json()
        
        # Validate that the core chart result contains data arrays
        if not data.get("chart", {}).get("result"):
            raise HTTPException(status_code=404, detail="Empty market metrics array returned.")
            
        result = data["chart"]["result"][0]
        meta = result.get("meta", {})
        current_price = round(float(meta.get("regularMarketPrice", 0.0)), 2)
        
        closes = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
        
        # Filter out null values (happens on market holidays or halted symbols)
        chart_points = []
        day_idx = 1
        for i in range(len(closes)):
            if closes[i] is not None:
                chart_points.append({
                    "day": day_idx,
                    "price": round(float(closes[i]), 2)
                })
                day_idx += 1
                
        if not chart_points:
            raise HTTPException(status_code=404, detail="No historical closing milestones found.")
            
        return {
            "ticker": ticker.upper(),
            "current_price": current_price,
            "chart_points": chart_points
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market data mapping routing failure: {str(e)}")
