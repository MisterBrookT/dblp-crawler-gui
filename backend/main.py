from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware  # new import
from pydantic import BaseModel
import backend.mydblp as mydblp  # existing crawler module
# ...existing imports if any...

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CrawlRequest(BaseModel):
    confs: list[str]
    keywords: list[str]

def perform_crawl(confs: list[str], keywords: list[str]):
    # Override global parameters in mydblp
    mydblp.CONFS = confs
    mydblp.keywords = keywords
    paper_list = []
    for conf in mydblp.CONFS:
        paper_list += mydblp.searchConference(conf, mydblp.keywords)
    if paper_list:
        mydblp.savePaper2csv(paper_list, mydblp.FILE_NAME)
    # Optionally, log results or further processing...
    print(f"Crawled {len(paper_list)} papers.")

@app.post("/crawl")
def crawl_endpoint(data: CrawlRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(perform_crawl, data.confs, data.keywords)
    return {"message": "Crawling started in background."}

# ...existing code if any...
