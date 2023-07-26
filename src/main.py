import os

from dotenv import load_dotenv
import migrator.exporter as me
import migrator.importer as mi

if __name__ == '__main__':
    load_dotenv()

    api = mi.DrupalApi(
        base_url=os.getenv("DRUPAL_URL"),
        drupal_user=os.getenv("DRUPAL_USER"),
        drupal_user_password=os.getenv("DRUPAL_USER_PASSWORD")
    )

    for article in me.load_articles():
        article.extract_s9y_files()
        article.replace_file_urls(os.getenv("S9Y_UPLOADS_FOLDER"))

        uuid = api.create_article_skeleton(article)
        print("Created article <{}> in Drupal with uuid {}".format(article.title, uuid))
