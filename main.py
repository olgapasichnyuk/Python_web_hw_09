import json

import requests
from bs4 import BeautifulSoup

from models import Author, Quote

BASE_URL = 'http://quotes.toscrape.com/'
PAGE_AMOUNT = 10
JSON_QUOTES_FILE = "quotes.json"
JSON_AUTHORS_FILE = "authors.json"


def parse_data(base_url, page_amount):
    all_pages_urls = [f"{base_url}page/{i}/" for i in range(1, (page_amount + 1))]


    def parse_page(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        quotes = soup.find_all("div", class_="quote")
        for quote in quotes:
            quote_text = quote.find("span", class_="text").text
            quote_tags = [tag.text for tag in quote.find_all("a", class_="tag")]
            author_fullname = quote.find("small", class_="author").text

            url_author = base_url + quote.find("a")["href"]
            response = requests.get(url_author)
            author_soup = BeautifulSoup(response.content, 'html.parser')

            author_born_date = author_soup.find("span", class_="author-born-date").text
            author_born_location = author_soup.find("span", class_="author-born-location").text
            author_description = author_soup.find("div", class_="author-description").text.strip()

            authors = {"fullname": author_fullname,
                       "born_date": author_born_date,
                       "born_location": author_born_location,
                       "description": author_description}

            quotes = {"tags": quote_tags,
                      "author": author_fullname,
                      "quote": quote_text}

            return quotes, authors

    res_quotes = []
    res_authors = []

    for page_url in all_pages_urls:
        quote_dict, author_dict = parse_page(page_url)
        res_quotes.append(quote_dict)
        if author_dict not in res_authors:
            res_authors.append(author_dict)

    return res_quotes, res_authors


def dump_data_to_json(data: list, json_file_name: str):
    with open(json_file_name, "w") as file:
        json.dump(data, file, indent=4)




def main():
    quotes, authors = parse_data(BASE_URL, PAGE_AMOUNT)
    dump_data_to_json(quotes, JSON_QUOTES_FILE)
    dump_data_to_json(authors, JSON_AUTHORS_FILE)

    with open(JSON_AUTHORS_FILE, "r") as file:
        data = json.load(file)

    for author in data:
        Author(fullname=author["fullname"],
               born_date=author["born_date"],
               born_location=author["born_location"],
               description=author["description"]).save()



    with open(JSON_QUOTES_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    authors = Author.objects()
    for quot in data:
        for author in authors:
            if author.fullname == quot["author"]:
                author_reference_obj = author

        Quote(tags=quot["tags"],
              author=author_reference_obj,
              quote=quot["quote"]).save()


if __name__ == "__main__":
    main()
