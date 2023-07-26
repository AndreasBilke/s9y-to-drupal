from article import Article
import datetime
import psycopg
import os


def load_articles() -> Article:
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST", "localhost")
    db = os.getenv("DB_NAME", "postgres")

    c = pg_connect(user, password, db, host)

    for item in pg_load_article(c):
        yield Article(
            title=item["title"],
            created_at=item["created_at"],
            body=item["body"],
            extended_body=item["extended_body"]
        )

    c.close()


def pg_load_article(connection) -> dict:
    with connection.cursor() as entry_cursor:
        entry_cursor.execute(
            "SELECT id, title, body, extended, timestamp FROM serendipity_entries ORDER BY last_modified DESC LIMIT 1;")

        for r in entry_cursor:
            d = {
                "id": r[0],
                "title": r[1],
                "body": r[2],
                "extended_body": r[3],
                "created_at": datetime.datetime.fromtimestamp(r[4])
            }

            with connection.cursor() as category_cursor:
                category_cursor.execute(
                    "SELECT category_name FROM serendipity_entrycat as ec JOIN serendipity_category as c ON  ec.categoryid = c.categoryid WHERE ec.entryid = %s; ",
                    (d["id"],)
                )
                cats = list()
                for entry_category in category_cursor:
                    cats.append(entry_category[0])

                d["categories"] = cats

            yield d


def pg_connect(username: str, password: str, database: str, hostname: str):
    con = psycopg.connect(user=username,
                          password=password,
                          dbname=database,
                          host=hostname)

    return con
