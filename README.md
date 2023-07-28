# S9Y to Drupal Exporter

> **Note**
> This tool is still under development and not finished

This program helps in migrating a current s9y installation (as of writing: 2.4.0)
to a freshly created Drupal 10 instance.

It does the following jobs:

- Copy s9y articles (including s9y hosted images) to Drupal
- Assigning (and create) categories to articles

It does **not** migrate S9Y users to Drupal nor does it migrate any configuration
related things (like blog title, plugins, etc.)

## S9Y requirements

- Read access to Postgresql database of S9Y (MySQL should work completely the same but the python program uses psql driver)
- Read access to `/uploads` folder from S9Y

## Drupal requirements

The following modules needs to be activated

- Json API (activate create/delete/patch capabilities)
- HTTP Basic Auth (used user needs admin access to Drupal)

## Workflow

1. Extract articles (with categories) from S9Y database
2. Extract image references from body/extended body of articles
   1. (QS) Check for image existence in `uploads/` folder
   2. Mark images in body/extended body such that the URLs can be rewritten later
3. For each article (creation via API)
   1. Create article with title only (to obtain UUID of Drupal article)
   2. Upload embedded images. Link image with article. Rename image with `s9y-migration` prefix.
      Obtain image URL from API response
   3. (Local preprocessing) Rewrite image URLs in body/extended body to match Drupal URLs
   4. Update article body/extended body

## Tool usage

- Install required Python dependencies (see `pyproject.toml`)
- Copy `.env.example` to `.env` and update parameters accordingly
- Run `python src/export-import/main.py`