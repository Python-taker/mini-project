import requests
from bs4 import BeautifulSoup

url = "https://www.danawa.com/"
# =====================================================
# 0️⃣  공용 headers
# =====================================================
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}

response = requests.get(url, headers=headers)
response.raise_for_status()  # 에러 발생 시 예외

soup = BeautifulSoup(response.text, "html.parser")
div_category = soup.find('div', attrs={"id": "category"})
#print(div_category.get_text(strip=True))
a_category__list__btn = div_category.find_all("a", attrs={"class": "category__list__btn"})
a_href_list = []
for href in a_category__list__btn:
    href_txt = href['href']
    a_href_list.append(href_txt)
print(a_href_list)
#test = soup.find('div', attrs={"id": "categoryHoverLayer22"})
#print(test)
