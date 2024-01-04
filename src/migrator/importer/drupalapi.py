from dataclasses import dataclass
from ..data import Article

import requests


@dataclass
class DrupalApi:
    base_url: str
    drupal_user: str
    drupal_user_password: str

    tag_uuids: dict[str, str]
    author_uuid: dict[str, str]

    def __init__(self, base_url: str, drupal_user: str, drupal_user_password: str):
        self.base_url = base_url
        self.drupal_user = drupal_user
        self.drupal_user_password = drupal_user_password

        self.tag_uuids = dict()
        self.author_uuids = dict()

    def assign_tags(self, article: Article):
        """ Assign tags/categories to an article """

        request = {
          "data": {
            "type": "node--article",
            "id": article.uuid,
            "relationships": {
              "field_tags": {
                "data": [
                    {
                        "type": "taxonomy_term--tags",
                        "id": self.get_tag_uuid(tag_name)
                    } for tag_name in article.categories
                ]
              }
            }
          }
        }

        response = requests.patch(
            "{}/jsonapi/node/article/{}".format(self.base_url, article.uuid),
            json=request,
            auth=(self.drupal_user, self.drupal_user_password),
            headers={"Content-Type": "application/vnd.api+json"}
        )

        if response.status_code != 200:
            raise Exception("Expected HTTP ok for article <{}>.\n\nServer response is\n{}"
                            .format(article.title, response.text))

    def upload_files(self, article: Article, s9y_file_directory: str = ""):
        """ Uploads all files for each article """

        api_url = "{}/jsonapi/node/article/{}/field_image".format(self.base_url, article.uuid)
        # we need the file index here for finding the correct URL in the server response
        for num, file in enumerate(article.files):
            file_name_drupal = "s9y-migration-{}".format(file.original_file_name())
            response = requests.post(
                api_url,
                data=open("{}/{}".format(s9y_file_directory, file.original_file_name()), "rb"),
                auth=(self.drupal_user, self.drupal_user_password),
                headers={
                    "Content-Disposition": "file; filename=\"{}\")".format(file_name_drupal),
                    "Content-Type": "application/octet-stream"
                }
            )

            if response.status_code != 200:
                raise Exception("Expected HTTP create for article <{}>.\n\nServer response is\n{}"
                                .format(article.title, response.text))

            # get image path
            response_json = response.json()
            file_attributes = response_json["data"][num]["attributes"]
            if file_attributes["filename"] != file_name_drupal:
                raise Exception("Uploaded file <{}>, but cannot find it in server response".format(file_name_drupal))

            file.drupal_url = file_attributes["uri"]["url"]

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
                },
                "relationships": {
                    "uid": {
                        "data": {
                            "type": "user--user",
                            "id": self.get_author_uuid(article.author)
                        }
                    }
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

    def complete_article(self, article: Article):
        """ Updates body/summary for an already created article """

        # In S9Y there was a body and an extended body
        # In Drupal such a concept does not exist the same way. It has only a body
        # But: You can specify (an independent) summary block which behaves like
        # the body in s9y (seen in article list etc.)
        # Here we concat s9y body/extended body and let drupal do the summary creation on its own
        request = {
            "data": {
                "type": "node--article",
                "id": article.uuid,
                "attributes": {
                    "body": {
                        "value": "{}\n{}".format(article.body, article.extended_body),
                        "format": "full_html"
                    }
                }
            }
        }

        response = requests.patch(
            "{}/jsonapi/node/article/{}".format(self.base_url, article.uuid),
            json=request,
            auth=(self.drupal_user, self.drupal_user_password),
            headers={"Content-Type": "application/vnd.api+json"}
        )

        if response.status_code != 200:
            raise Exception("Expected HTTP ok for article <{}>.\n\nServer response is\n{}"
                            .format(article.title, response.text))

    def get_tag_uuid(self, tag_name: str) -> str:
        if tag_name in self.tag_uuids:
            return self.tag_uuids[tag_name]

        remote_uuid = self.get_tag_by_name(tag_name)
        if remote_uuid is None:
            self.tag_uuids[tag_name] = self.create_tag_by_name(tag_name)
        else:
            self.tag_uuids[tag_name] = remote_uuid

        return self.tag_uuids[tag_name]

    def get_tag_by_name(self, tag_name: str) -> str | None:
        """ Fetch UUID of a tag """

        response = requests.get(
            "{}/jsonapi/taxonomy_term/tags".format(self.base_url),
            params={"filter[name]": tag_name},
            headers={"Content-Type": "application/vnd.api+json"}
        )

        return DrupalApi.extract_uuid_by_name(tag_name, response)

    def create_tag_by_name(self, tag_name: str) -> str:
        """ Creates a tag  """

        request = {
            "data": {
                "type": "node--article",
                "attributes": {
                    "name": tag_name
                }
            }
        }

        response = requests.post(
            "{}/jsonapi/taxonomy_term/tags".format(self.base_url),
            json=request,
            auth=(self.drupal_user, self.drupal_user_password),
            headers={"Content-Type": "application/vnd.api+json"}
        )

        if response.status_code != 201:
            raise Exception("Expected HTTP create for tag <{}>.\n\nServer response is\n{}"
                            .format(tag_name, response.text))

        response_json = response.json()
        return response_json["data"]["id"]

    def get_author_uuid(self, author: str) -> str:
        if author in self.author_uuids:
            return self.author_uuids[author]

        remote_uuid = self.get_author_by_name(author)
        if remote_uuid is None:
            raise Exception("Could not find author <{}> in Drupal instance".format(author))

        self.author_uuids[author] = remote_uuid
        return self.author_uuids[author]

    def get_author_by_name(self, author: str) -> str | None:
        """ Fetch UUID of an author """

        response = requests.get(
            "{}/jsonapi/user/user".format(self.base_url),
            params={"filter[name]": author},
            auth=(self.drupal_user, self.drupal_user_password),
            headers={"Content-Type": "application/vnd.api+json"}
        )

        return DrupalApi.extract_uuid_by_name(author, response)

    @staticmethod
    def extract_uuid_by_name(author: str, response: requests.Response) -> str | None:
        if not response.ok:
            return None

        response_json = response.json()
        found_data = response_json["data"]

        # The query resulted in multiple data sets, which was not expected
        # Items should be unique
        if len(found_data) != 1:
            return None

        remote_name = found_data[0]["attributes"]["name"]
        if remote_name != author:
            return None

        return found_data[0]["id"]
