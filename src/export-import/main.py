import os

from dotenv import load_dotenv
from dbtools import *

if __name__ == '__main__':
    load_dotenv()

    for article in load_articles():
        article.extract_s9y_files(os.getenv("S9Y_UPLOADS_FOLDER"))
        print(article)
