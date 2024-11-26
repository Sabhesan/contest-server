# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import cloudscraper
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Codeforces API",
    description="API to fetch contest information from Codeforces",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class Contest(BaseModel):
    contest_name: str
    contest_date: str
    duration: str
    register_link: str
    registration_status: str
    participants: str

class ContestsResponse(BaseModel):
    success: bool
    message: str
    contests: List[Contest]
    last_updated: str

def scrape_with_cloudscraper():
    try:
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        response = scraper.get('https://codeforces.com/contests')
        
        if response.status_code == 200:
            return response.text
        return None
            
    except Exception as e:
        print(f"Cloudscraper error: {str(e)}")
        return None

def scrape_with_selenium():
    chromedriver_autoinstaller.install()
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get('https://codeforces.com/contests')
        wait = WebDriverWait(driver, 30)
        contests_table = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'datatable'))
        )
        time.sleep(5)
        return driver.page_source
        
    except Exception as e:
        print(f"Selenium error: {str(e)}")
        return None
    finally:
        driver.quit()

def parse_contests(html_content):
    contests = []
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        contests_table = soup.find('div', class_='datatable')
        
        if contests_table:
            contest_rows = contests_table.find_all('tr')[1:]  # Skip header row
            for row in contest_rows:
                cols = row.find_all('td')
                if len(cols) >= 6:
                    register_link_col = cols[5]
                    register_link = register_link_col.find("a")["href"] if register_link_col.find("a") else "Not available"
                    
                    contest = Contest(
                        contest_name=cols[0].text.strip(),
                        contest_date=cols[2].text.strip(),
                        duration=cols[3].text.strip(),
                        register_link=f"https://codeforces.com{register_link}" if register_link != "Not available" else register_link,
                        registration_status=cols[4].text.strip(),
                        participants=cols[5].text.strip()
                    )
                    contests.append(contest)
    except Exception as e:
        print(f"Error parsing contests: {str(e)}")
    
    return contests

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to Codeforces Contests API"}

@app.get("/codeforces", response_model=ContestsResponse, tags=["Contests"])
async def get_contests():
    # Try cloudscraper first
    html_content = scrape_with_cloudscraper()
    
    # If cloudscraper fails, try Selenium
    if not html_content:
        html_content = scrape_with_selenium()
    
    if not html_content:
        raise HTTPException(status_code=500, detail="Failed to retrieve contests data")
    
    contests = parse_contests(html_content)
    
    if not contests:
        raise HTTPException(status_code=404, detail="No contests found")
    
    return ContestsResponse(
        success=True,
        message="Contests retrieved successfully",
        contests=contests,
        last_updated=datetime.now().isoformat()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)