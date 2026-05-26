from fastapi import FastAPI, HTTPException
import yfinance as yf

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Yahoo Finance PSX Microservice is running!"}

@app.get("/stock/{ticker}")
def get_psx_stock(ticker: str):
    # Yahoo Finance tracks PSX stocks using the .KA extension
    yf_ticker = f"{ticker.upper()}.KA"
    
    try:
        # Fetch the stock data
        stock = yf.Ticker(yf_ticker)
        
        # Pull exactly 7 days of historical market data
        hist = stock.history(period="7d") 
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="Stock data not found on Yahoo Finance. Check the ticker.")
            
        # Extract the absolute latest closing price
        current_price = round(float(hist['Close'].iloc[-1]), 2)
        
        # Automatically build the graph coordinates from the 7-day history
        chart_points = []
        day_counter = 1
        for index, row in hist.iterrows():
            chart_points.append({
                "day": day_counter,
                "price": round(float(row['Close']), 2)
            })
            day_counter += 1
            
        return {
            "ticker": ticker.upper(),
            "current_price": current_price,
            "chart_points": chart_points
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching from Yahoo Finance: {str(e)}")
