import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import re, math

book_link = []
with open("catergory_links.csv", mode="r") as file:
    csv_reader = csv.reader(file)
    header = next(csv_reader)
    numbersOfPage = 0
    for row in csv_reader:
        url = row[0]
        print(url)
        nameOfCsvFile = url[36:] + ".csv"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:

            soup = BeautifulSoup(response.content, "html.parser")

            search_string = url[26:] + "?page="
            print("search_string", search_string)
            specific_links = soup.find_all('a', href=lambda href: href and search_string in href)
            print("specific_links", specific_links)

            page_numbers = []

            for link in specific_links:
                href = link['href']
                page_number = href.split('=')[-1]  
                page_numbers.append(int(page_number)) 

            numbersOfPage = max(page_numbers) if page_numbers else 0
            print("numbersOfPage", numbersOfPage)
        if numbersOfPage > 0:
            for page in range(1, numbersOfPage + 1):
                url = url + "?page=" + str(page)

                hea = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(url, headers=hea)

                if res.status_code == 200:

                    soup = BeautifulSoup(res.content, "html.parser")

                    books = soup.find_all("a", class_="bookTitle")

                    for book in books:
                        link = "https://www.goodreads.com" + book["href"]
                        print(link)
                        book_link.append(link)
                        print(len(book_link))
                print("page:   ",page)
        book_df = pd.DataFrame(book_link, columns=["link"])
        book_df.to_csv(nameOfCsvFile, index=False)
        book_link = []
        print(nameOfCsvFile)
