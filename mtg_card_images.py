#!/usr/bin/python3
import requests
import traceback
import bs4
import os
import shutil
import re
import argparse

GATHERER_TEMPLATE = "http://gatherer.wizards.com/Pages/Search/Default.aspx?name=+[{name}]"
IMAGE_URL_BASE = "http://gatherer.wizards.com/"
FILE_NAME_TEMPLATE = "{num}_{name}.{format}"
IMAGE_ID = re.compile(r"ctl00_ctl00_ctl00_MainContent_SubContent_SubContent.*_cardImage")

DONE_MSG = "{index:<5}| DONE | Image {text} created as {dest}."
FAIL_MSG = "{index:<5}| FAIL | Could not get {text}:"
SKIP_MSG = "{index:<5}| SKIP | Image for {text} already exists."

HELP = {
    "file": "The list (one per line) of card names to look for",
    "template": "The format for the names of images (use: {num}=download number, {name}=card name, {format}=image format)",
    "log": "File name to write logs to",
    "out": "Output directory",
}

rows = []

parser = argparse.ArgumentParser(description="Download card photos from Gatherer.")

parser.add_argument('file', help=HELP['file'])
parser.add_argument('--template', default=FILE_NAME_TEMPLATE, help=HELP['template'])
parser.add_argument('--out', help=HELP['out'])
args = parser.parse_args()

if args.out and args.template:
    FILE_NAME_TEMPLATE = args.out.strip('/') + '/' + args.template
elif args.out:
    FILE_NAME_TEMPLATE = args.out.strip('/') + '/' + FILE_NAME_TEMPLATE
elif args.template:
    FILE_NAME_TEMPLATE = args.template

with open(args.file, 'r') as names:
    for line in names:
        rows.append(line)

for index, row in enumerate(rows):
    file_dest = FILE_NAME_TEMPLATE.format(num=index, name=row, format='png')
    if os.path.exists(file_dest):
        print(SKIP_MSG.format(index=index, text=row.strip('\n')))
        continue
    
    req = requests.get(GATHERER_TEMPLATE.format(name=row))
    bs = bs4.BeautifulSoup(req.content, 'lxml')
   
    try:
        print(bs.text)
        image_url = bs.find('img', attrs={'id': IMAGE_ID})
        image_url = image_url['src'].replace('../', '')
        image_req = requests.get(IMAGE_URL_BASE + image_url)
        with open(file_dest, 'wb') as img_file:
            img_file.write(image_req.content)
            print(DONE_MSG.format(index=index, text=row.strip('\n'), dest=file_dest))
    except Exception as e:
        print(FAIL_MSG.format(index=index, text=row.strip('\n')))
        traceback.print_exc()
