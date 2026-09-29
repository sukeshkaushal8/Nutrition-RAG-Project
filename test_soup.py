from bs4 import BeautifulSoup
import re
with open('data/raw/harvard-kids-plate.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, "html.parser")
article = soup.find('article')
parent = article.parent
while parent:
    classes = parent.get('class', [])
    if classes:
        print(parent.name, classes)
    parent = parent.parent
