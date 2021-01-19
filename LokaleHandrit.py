"""
By Madita
Based on codes by Balduin Landolt.
See Github for more info.
Run with one to two command line parameter, that refer to the
xml-file on Handrit.is, and optionally to the page range.
"""

import requests
import lxml
from bs4 import BeautifulSoup
import urllib
from urllib import request
import os

import copy

# Insert URL(s) here. To harvest only specific images of one (!) manuscript, see below.

myURLList = ["https://handrit.is/is/manuscript/xml/Lbs02-0187-is.xml"]

def get_soup(url):
    sauce = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sauce, "xml")
    return soup

def clean_surface(soups):
    for soup in soups:
        for sub in soup.find_all('surface'):
            sub.decompose()
        yield soup

def get_graphic(item):
    graphic = item.find('graphic', {'mimeType':'jpg'})
    url = graphic.get('url')
    url = url.replace("THUMBNAIL", "SECONDARY_DISPLAY")
    url = "https://myndir.handrit.is/file/Handrit.is/"+url
    return url

def dictionarize(items, names):
    res = []
    name = names
    for item in items:
        number = item.get('n')
        graphic = get_graphic(item)
        res.append((number, graphic, name))
    return res

def do_it_my_way(links):
    for url in links:
        soup = get_soup(url)
        items = soup.find_all('surface')

        tag = soup.msDesc
        handritID = str(tag['xml:id'])
        name = handritID[0:-3]

        copies = [copy.copy(item) for item in items]
        cleaned_copies = clean_surface(copies)
        structure = dictionarize(cleaned_copies, name)
        yield url, structure

list_of_results = do_it_my_way(myURLList) 

def save_image(id, url, name):
    path = 'out/'+name+'/'
    if not os.path.isdir(path):
        os.mkdir(path)
    file_name = "{}___{}.jpg".format(name, id)
    response = request.urlopen(url)
    data = response.read()
    with open(path+file_name, 'wb') as file:
        file.write(data)

print("Running...")
print('\n------------------\n')

for url, result in list_of_results:

    print(url)
    for vals in result:
        id = vals[0]
        img = vals[1]
        name = vals[2]

        # To harvest pages in the range of 66 to 98, insert < 66 and > 98 in the following if-condition.
        # This works for one MS only (see myURLs above).
        # To download all images, comment out the following if-condition.

        page = int(id)
        if page < 420 or page > 465:
            continue

        save_image(id, img, name)
    print('\n------------------\n')

print("Done.")