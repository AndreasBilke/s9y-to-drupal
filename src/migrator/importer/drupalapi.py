from dataclasses import dataclass
from ..data import Article, File

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

    def create_article_skeleton(self, article: Article) -> str:
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

        return response_json["data"]["id"]
