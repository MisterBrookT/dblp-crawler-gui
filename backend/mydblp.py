# %%
import requests
from bs4 import BeautifulSoup
import re
import csv
import logging
import argparse
import os


# parameters
keywords = ["train"]  
CONFS = ["fast",]
SCORE_EACH_KEYWORD = 1
YEAR_START = 2023
SCORE_THRESHOD = 1
FILE_NAME = "data.csv"

class Paper():
    def __init__(self, title=None, venue=None, year=None, pages=None):
        self.title = title
        self.venue = venue
        self.year = year
        self.pages = pages
        self.authors = []
        self.score = None

    # in this func, we treat all keyword weight equal   
    def calScore(self):
        s = 0
        for keyword in keywords:
            if keyword in self.title.lower():
                # s += keywords[keyword]
                s += SCORE_EACH_KEYWORD
        self.score = s

    def __str__(self):
        assert self.title is not None
        assert self.venue is not None
        assert self.year is not None
        return "{} {}, {} {}".format(self.title, self.pages, self.venue, self.year)


def savePaper2csv(paper_list, FILE_NAME):
    with open("{}".format(FILE_NAME), "w") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "venue", "year", "pages", "authors"])
        for paper in paper_list:
            writer.writerow([paper.title, paper.venue, paper.year, paper.pages, ", ".join(i for i in paper.authors)])


def getContentStrings(tag):
    tmp = ""
    for c in tag.contents:
        clen = 0
        try:
            clen = len(c.contents)
        except AttributeError:
            clen = 0
        if clen:
            cstr = getContentStrings(c)
            tmp += cstr
        else:
            tmp += c.string
    return tmp

def searchConference(conf, keywords):
    print(f"\nsearch {conf}")
    dblp_url = "https://dblp.org/search/publ/inc"
    confre = re.compile(".*{}.*".format(conf), re.IGNORECASE)

    search_word = "|".join(i for i in keywords)
    print(search_word)
    search_word += " streamid:conf/{}:".format(conf)

    page = 0
    year = 0
    year_smaller_bool = False
    paper_list = []
    while True:
        payload = {
                "q": search_word,
                "s": "ydvspc",
                "h": "1000",
                "b": "{}".format(page),
            }
        r = requests.get(dblp_url, params=payload)
        print("Request {} 1000 records the {} time".format(conf, page+1))
        soup = BeautifulSoup(r.text, "html.parser")
        record_list = soup.find_all("li", class_=re.compile("year|inproceedings"))
        if len(record_list) == 0:
            print("No more paper can be found!")
            break
        for idx, record in enumerate(record_list):
            if "year" in record["class"]:
                year = int(record.string)
                print("Find year record {}.".format(year))
                if year < YEAR_START:
                    year_smaller_bool = True
                    print("Current year smaller than YEAR_START! Finish finding paper list.")
                    break
                continue
            if "inproceedings" not in record["class"]:
                print("No inproceedings in record class: {}".format(record["class"]))
                continue
            # try:
            authors = record.cite.find_all(itemprop="author")
            title_tag = record.cite.find(class_="title")
            paper_title = getContentStrings(title_tag)
            paper_venue = record.cite.find(itemprop="isPartOf").string
            if not re.match(confre, paper_venue):
                print("Ignore {}".format(paper_venue))
                continue
            paper_pagination = record.cite.find(itemprop="pagination")
            if paper_pagination:
                paper_pagination = paper_pagination.string
            else:
                print("Paper with no pagination. venue: {}".format(paper_venue))
            
            pp = Paper(title=paper_title, venue=paper_venue, year=year, pages=paper_pagination)
            for author in authors:
                try:
                    pp.authors.append(author.a.string)
                except AttributeError:
                    print("Unable to append author: 'NoneType' object has no attribute 'string'")  
                    continue
                
            pp.calScore()

            if pp.score >= SCORE_THRESHOD:
                paper_list.append(pp)
        if year_smaller_bool:
            break

    print("Find {} papers".format(len(paper_list)))
    return paper_list


if __name__ == "__main__":
    paper_list = []
    for conf in CONFS:
        # for keywords in keywords_list:
            paper_list += searchConference(conf, keywords)
            if len(paper_list):
                savePaper2csv(paper_list, FILE_NAME)
                print("paper list saved to {}".format(FILE_NAME))

