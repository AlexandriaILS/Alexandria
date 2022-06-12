import glob
import json
import sqlite3

from django.core.management.base import BaseCommand
from rich.progress import track


def setup_dump_db():
    con = sqlite3.connect("ol_dump.sqlite3")
    cur = con.cursor()
    cur.execute(
        "create table if not exists authors (name text, ol_id text, unique(name, ol_id))"
    )
    # author_ids is a pipe separated string, as is subjects
    cur.execute(
        "create table if not exists works"
        " (title text, author_ids text, subjects text, unique(title, author_ids))"
    )
    cur.execute("create table if not exists subjects (name text unique)")
    con.commit()
    return con


class Command(BaseCommand):
    help = "Create ol_dump database from OpenLibrary dump files."

    def handle(self, *args, **options):
        download_error_message = (
            "Missing {} file -- download from https://openlibrary.org/developers/dumps,"
            " unzip it into the top level directory for Alexandria (with manage.py) and"
            " try this command again."
        )
        too_many_files_message = (
            "Found more than {} file -- please delete all but the most recent and try"
            "again."
        )

        works_file_list = glob.glob("ol_dump_works*.txt")
        authors_file_list = glob.glob("ol_dump_authors*.txt")
        if not works_file_list:
            raise Exception(download_error_message.format("ol_dump_works"))
        if not authors_file_list:
            raise Exception(download_error_message.format("ol_dump_authors"))

        if len(works_file_list) > 1:
            raise Exception(too_many_files_message.format("ol_dump_works"))
        if len(authors_file_list) > 1:
            raise Exception(too_many_files_message.format("ol_dump_authors"))

        works_file = works_file_list[0]
        authors_file = authors_file_list[0]

        con = setup_dump_db()
        batch_size = 500

        def get_chunk(buf, n):
            """Read n-line chunks from filehandle."""
            while buf:
                chunk = [buf.readline() for _ in range(n)]
                if not any(chunk):
                    chunk = None
                yield chunk

        count = 0
        with open(authors_file) as chunk_data:
            for chunk in track(
                get_chunk(chunk_data, batch_size),
                description="[green]Writing author data...",
            ):
                if not chunk:
                    break

                author_groups = []
                for line in chunk:
                    try:
                        raw_data = json.loads(line.split("\t")[-1].strip())
                        author_groups.append(
                            (raw_data["name"], raw_data["key"].split("/")[2])
                        )
                    except:
                        ol_id = raw_data["key"].split("/")[2]
                        if name := raw_data.get("personal_name"):
                            author_groups.append((name, ol_id))
                        if name := raw_data.get("fuller_name"):
                            author_groups.append((name, ol_id))
                        continue

                cur = con.cursor()
                cur.executemany(
                    "insert into authors values (?, ?) on conflict do nothing",
                    author_groups,
                )
                con.commit()
                chunk_size = len(chunk)
                if chunk_size < batch_size:
                    count += chunk_size
                else:
                    count += batch_size

        self.stdout.write(f"Wrote {count} authors. Beginning export of works.")

        count = 0
        errors = []
        with open(works_file) as chunk_data:
            for chunk in track(
                get_chunk(chunk_data, batch_size), "[green]Writing works data..."
            ):
                if not chunk:
                    break

                works_list = []
                subjects_list = []
                for line in chunk:
                    try:
                        raw_data = json.loads(line.split("\t")[-1].strip())
                        title = raw_data.get("title")
                        if not title:
                            continue
                        title = title.encode().decode()  # handle international chars
                        subjects = raw_data.get("subjects", None)
                        if subjects:
                            for i in subjects:
                                subjects_list.append((i.encode().decode(),))
                            subjects = "|".join(subjects).encode().decode()

                        author_objs: list[dict] = raw_data.get("authors", None)
                        if author_objs:
                            try:
                                author_ids = "|".join(
                                    [
                                        a["author"]["key"].split("/")[2]
                                        for a in author_objs
                                    ]
                                )
                            except:
                                # malformed authors line. This represents roughly 40k
                                # records. Sucks, but can't fix missing data.
                                count -= 1
                                continue
                        works_list.append((title, author_ids, subjects))
                    except:
                        count -= 1
                        errors.append(line)

                cur = con.cursor()
                cur.executemany(
                    "insert into works values (?, ?, ?) on conflict do nothing",
                    works_list,
                )
                cur.executemany(
                    "insert into subjects values (?) on conflict do nothing",
                    subjects_list,
                )
                con.commit()

                chunk_size = len(chunk)
                if chunk_size < batch_size:
                    count += chunk_size
                else:
                    count += batch_size

        self.stdout.write(f"Wrote {count} works, {len(errors)} errors.")
        with open("errors.txt", "w") as f:
            f.write("\n".join(errors))
        self.stdout.write(f"Done!")
