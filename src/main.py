import argparse
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
import os

import migrator.exporter as me
import migrator.importer as mi

if __name__ == '__main__':
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="s9y to drupal migrator",
        description="Extracts blog articles from a s9y database and re-creates them in drupal"
    )
    parser.add_argument("-f", "--date-from",
                        default=date.today(),
                        help="Articles with creation date larger than this date. Format YYYY-MM-DD",
                        type=lambda s: datetime.strptime(s, "%Y-%m-%d").date()
                        )
    parser.add_argument("-t", "--date-to",
                        default=date.today() + timedelta(days=1),
                        help="Articles with creation date smaller than this date. Format YYYY-MM-DD",
                        type=lambda s: datetime.strptime(s, "%Y-%m-%d").date()
                        )

    args = parser.parse_args()

    api = mi.DrupalApi(
        base_url=os.getenv("DRUPAL_URL"),
        drupal_user=os.getenv("DRUPAL_USER"),
        drupal_user_password=os.getenv("DRUPAL_USER_PASSWORD")
    )

    s9y_upload_folder = os.getenv("S9Y_UPLOADS_FOLDER")
    for article in me.load_articles(args.date_from, args.date_to):
        try:
            article.extract_s9y_files()
            article.replace_file_urls(s9y_upload_folder)

            api.create_article_skeleton(article)
            api.upload_files(article, s9y_upload_folder)
            article.replace_links()
            api.complete_article(article)
            api.assign_tags(article)

            print("Created article <{}> in Drupal with uuid {}".format(article.title, article.uuid))
        except Exception as e:
            print("Error while migration article for <{}>. Message:\n{}".format(article.title, e))
