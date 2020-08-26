import re
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup


def get_korean_tag(page):

    url = 'https://top-hashtags.com/instagram/{}/'.format(page)

    res = requests.get(url)

    bs = BeautifulSoup(res.text, 'html.parser')
    tags = bs.select('div.entry-content ul li div.i-tag')

    print(tags)
    korean_tag = []
    for tag in tags:
        if re.match("#[가-힣].+", tag):
            korean_tag.append(tag)
        else:
            pass

    print(korean_tag)
    return korean_tag

# korean_tag_list = []
#
# for num in tqdm(range(9999)):
#     i = num * 100 + 1
#     korean_tag_list.extend(get_korean_tag(i))
#     # print(korean_tag_list)
#
#
# print("fianl!!!")
# print(korean_tag_list)

print(get_korean_tag(999901))