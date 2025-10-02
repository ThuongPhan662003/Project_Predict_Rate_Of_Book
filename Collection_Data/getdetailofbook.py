import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
import time


def get_followers(author_link):
    global count 
    print(f"Đang cào thêm từ link {author_link}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(author_link, headers=headers)
        response.raise_for_status() 
        soup = BeautifulSoup(response.content, 'html.parser')
        h2_tags = soup.find_all('h2', class_='brownBackground')

        for h2 in h2_tags:
            if 'Followers' in h2.get_text():
                followers_text = h2.get_text(strip=True)
                followers_count = followers_text.split('(')[-1].split(')')[0].replace(',', '')
                count += 1  
                print(f"Đã cào được {count} lần")
                return int(followers_count)
        return None  
    except Exception as e:
        print(f"Lỗi khi cào {author_link}: {e}")
        return None

def get_genres_and_votes(link,genre_list):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(link, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        html_content = response.text

        pattern = re.compile(r'https://www\.goodreads\.com/work/shelves/(\d+)-[^"]+')
        match = pattern.search(html_content)

        if match:
            work_id = match.group(1)
            genre_url = f"https://www.goodreads.com/work/shelves/{work_id}"

            genre_response = requests.get(genre_url, headers=headers)
            genre_soup = BeautifulSoup(genre_response.content, "html.parser")
            shelves = genre_soup.find_all("div", class_="shelfStat")

            genres_and_votes = []

            for shelf in shelves:
                genre_tag = shelf.find("a", class_="mediumText actionLinkLite")
                votes_tag = shelf.find("div", class_="smallText")
                if genre_tag and votes_tag:
                    genre = genre_tag.text.strip()
                    formatted_str = ' '.join(word.capitalize() for word in genre.split('-'))
                    votes_text = votes_tag.text.strip()
                    votes = int(votes_text.split()[0].replace(",", ""))
                    if formatted_str in genre_list:
                        genres_and_votes.append((formatted_str, votes))
            genre_and_vote = ", ".join(
                [f"{genre} {votes}" for genre, votes in genres_and_votes]
            )
            return genre_and_vote
        else:
            return ""
    else:
        print(f"Failed to retrieve genres and votes for link: {link}")
        return ""


# Hàm để lấy thông tin chi tiết của một cuốn sách từ đường link
def get_book_details(link, book_id):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(link, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        html_content = response.text  # Lưu nội dung HTML
        # Xử lý id của cuốn sách
        pattern = re.compile(r"/show/(\d+)")
        match = pattern.search(link)

        id = match.group(1) if match else ""
        if not id:
            print(f"ID not found for link: {link}")
        # Lấy tên của cuốn sách
        title_tag = soup.find("h1", {"data-testid": "bookTitle"})
        title = title_tag.text.strip() if title_tag else None

        # Lấy series (nếu có) của cuốn sách
        series_tag = soup.find("a", href=lambda x: x and "/series/" in x)
        series = series_tag.text.strip() if series_tag else None

        # Lấy tên tác giả
        author_tag = soup.find("a", class_="ContributorLink")
        author = (
            author_tag.find("span", {"data-testid": "name"}).text.strip()
            if author_tag
            else None
        )

        # Lấy link dẫn đến trang tác giả
        author_link = (
            author_tag["href"] if author_tag and "href" in author_tag.attrs else None
        )
        if author_link and not author_link.startswith("http"):
            author_link = "https://www.goodreads.com" + author_link

        # Lấy đánh giá trung bình
        rating_tag = soup.find("span", itemprop="ratingValue")
        rating = rating_tag.text.strip() if rating_tag else None

        # Lấy số lượng đánh giá
        rating_count_tag = soup.find("span", {"data-testid": "ratingsCount"})
        rating_count_text = rating_count_tag.text.strip() if rating_count_tag else None
        rating_count = (
            rating_count_text.split()[0].replace(",", "") if rating_count_text else None
        )

        # Lấy số lượng review
        review_count_tag = soup.find("span", {"data-testid": "reviewsCount"})
        review_count_text = review_count_tag.text.strip() if review_count_tag else None
        review_count = (
            review_count_text.split()[0].replace(",", "") if review_count_text else None
        )

        # Lấy số trang
        pages_tag = soup.find("p", {"data-testid": "pagesFormat"})
        number_of_pages = pages_tag.text.strip().split()[0] if pages_tag else None

        # Lấy ngày xuất bản
        publication_info_tag = soup.find("p", {"data-testid": "publicationInfo"})
        date_published = (
            publication_info_tag.text.strip().replace("First published ", "")
            if publication_info_tag
            else None
        )

        # Lấy thông tin nhà xuất bản
        pattern = re.compile(r'"publisher":\s*"([^"]+)"', re.DOTALL)
        match = pattern.search(html_content)
        publisher = match.group(1) if match else None
        if publisher:
            publisher = publisher.encode('utf-8').decode('unicode_escape')
        

        # Lấy isbn và isbn13 của cuốn sách

        isbn13_match = re.search(r'"isbn13":"(\d{13})"', html_content)
        isbn13 = isbn13_match.group(1) if isbn13_match else ""
        isbn_match = re.search(r'"isbn":"(\d{10})"', html_content)
        isbn = isbn_match.group(1) if isbn_match else ""
        # Lấy settings của cuốn sách
        pattern = re.compile(r'"places":(\[.*?\])', re.DOTALL)
        match = pattern.search(html_content)

        if match:
            settings_json_str = match.group(1)
            settings_data = json.loads(settings_json_str)
            setting_names = [setting["name"] for setting in settings_data]
            settings = ", ".join(setting_names)
        else:
            settings = ""
            print(f"Settings not found for link: {link}")
        # Lấy characters của cuốn sách
        pattern = re.compile(r'"characters":(\[.*?\])', re.DOTALL)
        match = pattern.search(html_content)

        characters = ""
        if match:
            characters_json_str = match.group(1)
            characters_data = json.loads(characters_json_str)
            character_names = [characters["name"] for characters in characters_data]
            characters = ", ".join(character_names)
        else:
            print(f"Characters not found for link: {link}")

        # Nếu tìm thấy, phân tích cú pháp JSON
        if match:
            genres_json_str = match.group(1)
            genres_data = json.loads(genres_json_str)

            # Lấy tên thể loại và URL
        # Lấy genre_and_votes
        pattern = re.compile(r'"bookGenres":(\[.*?\])', re.DOTALL)
        match = pattern.search(html_content)
        names =[]
        # Nếu tìm thấy, phân tích cú pháp JSON
        if match:
            genres_json_str = match.group(1)
            genres_data = json.loads(genres_json_str)

            # Lấy tên thể loại và URL
            genres = [
                (genre["genre"]["name"], genre["genre"]["webUrl"])
                for genre in genres_data
            ]
            
            for name, url in genres:
                names.append(name)
        else:
            genre_and_votes = ""
        
        genre_and_votes = get_genres_and_votes(link,names)

        # Lấy đánh giá trung bình từ thẻ <div class="RatingStatistics__rating">
        rating_tag = soup.find("div", class_="RatingStatistics__rating")
        rating = rating_tag.text.strip() if rating_tag else None

        # Lấy tên của cuốn sách
        title_tag = soup.find("h1", {"data-testid": "bookTitle"})
        original_title = title_tag.text.strip() if title_tag else ""
        if not original_title:
            print(f"Original title not found for link: {link}")

        # Lấy mô tả cuốn sách
        description_tag = soup.find("span", class_="Formatted")
        description = description_tag.text.strip() if description_tag else None

        # Lấy giải thưởng (awards)
        awards_pattern = re.compile(r'"awardsWon":(\[.*?\])', re.DOTALL)
        match = awards_pattern.search(html_content)
        awards = []
        if match:
            awards_json_str = match.group(1)
            awards_data = json.loads(awards_json_str)
            awards = [award["name"] for award in awards_data]

        return {
            "": book_id,
            "id": id,
            "link": link,
            "series": series,
            "author": author,
            "author_link": author_link,
            "rating_count": rating_count,
            "review_count": review_count,
            "number_of_pages": number_of_pages,
            "date_published": date_published,
            "publisher": publisher,
            "original_title": original_title,
            "genre_and_votes": genre_and_votes,
            "isbn": isbn,
            "isbn13": isbn13,
            "settings": settings,
            "characters": characters, 
            "description": description,
            "title": title,
            "awards": awards,
            "rating": rating,

        }
    else:
        return None


books_data = []
ratings_data = []

book_links_df = pd.read_csv("get2.csv")  
try:
    for idx, row in book_links_df.iterrows():
        link = row["link"]  
        book_id = idx + 1  # Tạo ID cho mỗi cuốn sách (từ 1 đến n)
        print(f"Đang lấy thông tin từ: {link}")
        
        data = get_book_details(link,book_id)
        
        if data:  
            book_data = {
                    "": book_id,
                    "id": data["id"],
                    "link": data["link"],
                    "series": data["series"],
                    "author": data["author"],
                    "author_link": data["author_link"],
                    "rating_count": data["rating_count"],
                    "review_count": data["review_count"],
                    "number_of_pages": data["number_of_pages"],
                    "date_published": data["date_published"],
                    "publisher": data["publisher"],
                    "original_title": data["original_title"], 
                    "genre_and_votes": data["genre_and_votes"],
                    "isbn": data["isbn"],
                    "isbn13": data["isbn13"],
                    "settings": data["settings"], 
                    "characters": data["characters"], 
                    "description": data["description"],
                    "title": data["title"],
                    "awards": data["awards"],
                    "followers": get_followers(data["author_link"])

            }
            print(book_data)
            rating_data = {
                "":data[""],
                "id":data["id"],
                "rating":data["rating"]
            }
        if book_data:
            books_data.append(
                book_data
            )  

        
        if rating_data:
            ratings_data.append(
                rating_data
            )  
        print(book_id)
        time.sleep(1)
except Exception as e:
    books_df = pd.DataFrame(books_data) 
    books_df.to_csv(
        "book_details.csv", index=False, encoding="utf-8"
    ) 
    rating_df = pd.DataFrame(ratings_data)
    rating_df.to_csv("rating.csv", index=False)
    print(f"Error processing book {book_id} from {link}: {e}")

books_df = pd.DataFrame(books_data) 
books_df.to_csv(
    "book_details.csv", index=False, encoding="utf-8"
) 
rating_df = pd.DataFrame(ratings_data)
rating_df.to_csv("rating_2.csv", index=False)
print("Đã lưu thông tin sách vào file 'book_details.csv'.")

