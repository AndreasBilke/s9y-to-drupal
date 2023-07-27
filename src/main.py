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

    s9y_upload_folder = os.getenv("S9Y_UPLOADS_FOLDER")
    for article in me.load_articles():
        article.extract_s9y_files()
        article.replace_file_urls(s9y_upload_folder)

        api.create_article_skeleton(article)
        api.upload_files(article, s9y_upload_folder)
        print("Created article <{}> in Drupal with uuid {}".format(article.title, article.uuid))
