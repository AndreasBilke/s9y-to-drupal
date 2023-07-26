import datetime
import os.path
import sys
from dataclasses import dataclass
import re


@dataclass()
class File:
    """ Represents an uploaded file within a blog """
    name: str
    ext: str
    is_thumb: bool

    def __init__(self, name: str, ext: str, is_thumb: bool):
        self.name = name
        self.ext = ext
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

    def extract_s9y_files(self):
        thumbnail_pattern = r"[\"']\/uploads\/(\w+)\.serendipityThumb\.(\w+)[\"']"

        thumbs = re.findall(thumbnail_pattern, self.body)
        self.create_file_entries(thumbs, is_thumbnail=True)
        thumbs = re.findall(thumbnail_pattern, self.extended_body)
        self.create_file_entries(thumbs, is_thumbnail=True)

        image_pattern = r"[\"']\/uploads\/(\w+)\.(\w+)[\"']"
        images = re.findall(image_pattern, self.body)
        self.create_file_entries(images)
        images = re.findall(image_pattern, self.extended_body)
        self.create_file_entries(images)

    def create_file_entries(self, items: list[tuple], is_thumbnail: bool = False):
        for item in items:
            if len(item) != 2:
                continue

            f = File(
                name=item[0] if item[0] is not None else "",
                ext=item[1] if item[1] is not None else "",
                is_thumb=is_thumbnail
            )

            if f not in self.files:
                self.files.append(f)

    def replace_file_urls(self, s9y_file_directory: str = ""):
        bogus_files = []

        for file in self.files:
            if file.is_thumb:
                original_file_name = "{}.serendipityThumb.{}".format(file.name, file.ext)
                http_path = "/uploads/{}".format(original_file_name)
                replace_prefix = "<IMAGE_URL_THUMBNAIL>"
            else:
                original_file_name = "{}.{}".format(file.name, file.ext)
                http_path = "/uploads/{}".format(original_file_name)
                replace_prefix = "<IMAGE_URL>"

            image_path = "{}/{}.{}".format(replace_prefix, file.name, file.ext)

            self.body = self.body.replace(http_path, image_path)
            self.extended_body = self.extended_body.replace(http_path, image_path)

            fs_image_path = "{}/{}".format(s9y_file_directory, original_file_name)
            if not os.path.isfile(fs_image_path):
                bogus_files.append(file)

                print("File <{}> was in article <{}> but is not found on file system"
                      .format(original_file_name, self.title), file=sys.stderr)

        for bogus_file in bogus_files:
            self.files.remove(bogus_file)

