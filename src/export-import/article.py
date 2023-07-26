import datetime
from dataclasses import dataclass
import re


@dataclass()
class File:
    """ Represents an uploaded file within a blog """
    name: str
    is_thumb: bool

    def __init__(self, name: str, is_thumb: bool):
        self.name = name
        self.is_thumb = is_thumb


@dataclass()
class Article:
    """Represents an article within a blog"""

    title: str
    created_at: datetime.datetime
    body: str
    extended_body: str
    files: list[File]  # list of filenames which are used in this article

    def __init__(self, title: str, created_at: datetime.datetime, body: str, extended_body: str):
        self.title = title
        self.created_at = created_at
        self.body = body
        self.extended_body = extended_body

        self.files = list()

    def extract_s9y_files(self, s9y_file_directory: str = ""):
        thumbnail_pattern = "[\"\']\\\\/uploads\\\\/(\\S)\\.serendipityThumb\\.(\\S)[\"\']"
        thumbs = re.findall(thumbnail_pattern, self.body)
        print(thumbs)
        self.create_file_entries(thumbs, is_thumbnail=True)
        thumbs = re.findall(thumbnail_pattern, self.extended_body)
        print(thumbs)
        self.create_file_entries(thumbs, is_thumbnail=True)

        image_pattern = "[\"\']\\\\/uploads\\\\/(\\S)\\.(\\S)[\"\']"
        images = re.findall(image_pattern, self.body)
        print(images)
        self.create_file_entries(images)
        images = re.findall(image_pattern, self.extended_body)
        print(images)
        self.create_file_entries(images)

    def create_file_entries(self, items: list[tuple], is_thumbnail: bool = False):
        for item in items:
            f = File(
                name="%s.%s".format(item[0], item[1]),
                is_thumb=is_thumbnail
            )

            self.files.append(f)
