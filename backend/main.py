from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import backend.mydblp as mydblp
import os
import json
from typing import List, Optional

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track crawl status
crawl_status = {
    "in_progress": False,
    "completed": False,
    "paper_count": 0,
    "error": None
}

class CrawlRequest(BaseModel):
    confs: List[str]
    keywords: List[str]
    year_start: int = 2023

def perform_crawl(confs: List[str], keywords: List[str], year_start: int):
    global crawl_status
    crawl_status = {
        "in_progress": True,
        "completed": False, 
        "paper_count": 0,
        "error": None
    }
    
    try:
        # Override global parameters in mydblp
        mydblp.CONFS = confs
        mydblp.keywords = keywords
        mydblp.YEAR_START = year_start
        
        paper_list = []
        for conf in confs:
            paper_list += mydblp.searchConference(conf, keywords)
            
        if paper_list:
            mydblp.savePaper2csv(paper_list, mydblp.FILE_NAME)
            crawl_status["paper_count"] = len(paper_list)
        
        crawl_status["completed"] = True
    except Exception as e:
        crawl_status["error"] = str(e)
    finally:
        crawl_status["in_progress"] = False

@app.post("/crawl")
def crawl_endpoint(data: CrawlRequest, background_tasks: BackgroundTasks):
    if crawl_status["in_progress"]:
        raise HTTPException(status_code=400, detail="A crawl is already in progress")
    
    background_tasks.add_task(perform_crawl, data.confs, data.keywords, data.year_start)
    return {"message": "Crawling started in background."}

@app.get("/status")
def status_endpoint():
    return crawl_status

@app.get("/download")
def download_endpoint():
    if not os.path.exists(mydblp.FILE_NAME):
        raise HTTPException(status_code=404, detail="No results file available")
    return FileResponse(mydblp.FILE_NAME, media_type="text/csv", filename="dblp_results.csv")

@app.get("/results")
def results_endpoint(limit: Optional[int] = 100, offset: Optional[int] = 0):
    """Return paginated results from the CSV file"""
    if not os.path.exists(mydblp.FILE_NAME):
        raise HTTPException(status_code=404, detail="No results file available")
    
    import csv
    results = []
    total_count = 0
    
    with open(mydblp.FILE_NAME, 'r') as f:
        reader = csv.DictReader(f)
        # Count total records
        rows = list(reader)
        total_count = len(rows)
        
        # Apply pagination
        paginated_rows = rows[offset:offset + limit]
        results = paginated_rows
    
    return {
        "total": total_count,
        "results": results
    }

@app.get("/conferences")
def conferences_endpoint():
    """Return predefined conference groups"""
    # Load conferences from the JSON file
    with open(os.path.join(os.path.dirname(__file__), 'conferences.json'), 'r') as f:
        return json.load(f)

