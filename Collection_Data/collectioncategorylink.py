import requests
from bs4 import BeautifulSoup
import pandas as pd
catergory_links = []
for i in range(1,101):
    
    url = 'https://www.goodreads.com/list/recently_active_lists?page='+str(i)

    headers = {'User-Agent': 'Mozilla/5.0'} 
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        catergorys = soup.find_all('a', class_='listTitle')
        for catergory in catergorys:
            link = 'https://www.goodreads.com' + catergory['href']
            catergory_links.append(link)

        if i==100:
            print("Danh sách link đã được lưu vào file 'catergory_links.csv'.")
    else:
        print(f"Yêu cầu thất bại lần {i} với mã lỗi: {response.status_code}")
book_df = pd.DataFrame(catergory_links, columns=['link'])
book_df.to_csv('catergory_links.csv', index=False)
