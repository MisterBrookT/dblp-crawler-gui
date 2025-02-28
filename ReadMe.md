## dblp crawler

### Install python environment

Use `pip install -r requirements.txt` to install runtime requirements.

Use `pip install -r requirements-dev.txt` to install development requirements.

### Features

Crawl papers for specific conferences in dblp with multiple keywords.

- [X] Crawl conference
- [X] Simple regex to filter workshop or other session
- [X] Log to a file and stream to console

### Usage

Activate your virtual environment and run:

cd backend

uvicorn main:app

`python mydblp.py -h` for the help message.

`python mydblp.py --conf="sc"` to crawl a specific conference.

### Things to be implemented

- [ ] Crawl journal
- [ ] Multi-processing crawl
- [ ] Add more regex filters
- [ ] Read keywords from a json file
- [ ] More
