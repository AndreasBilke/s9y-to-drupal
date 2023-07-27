from dataclasses import dataclass
from ..data import Article

import requests


@dataclass
class DrupalApi:
    base_url: str
    drupal_user: str
    drupal_user_password: str

    def __init__(self, base_url: str, drupal_user: str, drupal_user_password: str):
        self.base_url = base_url
        self.drupal_user = drupal_user
        self.drupal_user_password = drupal_user_password

    def upload_files(self, article: Article, s9y_file_directory: str = ""):
        """ Uploads all files for each article """

        api_url = "{}/jsonapi/node/article/{}/field_image".format(self.base_url, article.uuid)
        for file in article.files:
            response = requests.post(
                api_url,
                data=open("{}/{}".format(s9y_file_directory, file.original_file_name()), "rb"),
                auth=(self.drupal_user, self.drupal_user_password),
                headers={
                    "Content-Disposition": "file; filename=\"s9y-migration-{}\"".format(file.original_file_name()),
                    "Content-Type": "application/octet-stream"
                }
            )

            if response.status_code != 200:
                raise Exception("Expected HTTP create for article <{}>.\n\nServer response is\n{}"
                                .format(article.title, response.text))

            # get image path
            response_json = response.json()
            path = response_json["data"][0]["attributes"]["uri"]["url"]

            file.drupal_url = path

    def create_article_skeleton(self, article: Article):
        """ Creates an article (just with title) but returns the UUID for further usage """

        request = {
            "data": {
                "type": "node--article",
                "attributes": {
                    "title": article.title,
                    # TODO I'm cheating here because I know the TZ offset for my instances
                    "created": article.created_at.strftime("%Y-%m-%dT%H:%M:%S+02:00"),
                    "body": {}
                }
            }
        }

        response = requests.post(
            "{}/jsonapi/node/article".format(self.base_url),
            json=request,
            auth=(self.drupal_user, self.drupal_user_password),
            headers={"Content-Type": "application/vnd.api+json"}
        )

        if response.status_code != 201:
            raise Exception("Expected HTTP create for article <{}>.\n\nServer response is\n{}"
                            .format(article.title, response.text))

        response_json = response.json()
        article.uuid = response_json["data"]["id"]
