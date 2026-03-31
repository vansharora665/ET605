from __future__ import annotations

from app.db.session import SessionLocal, init_db
from app.models import Chapter, Subtopic
from app.services.catalog import load_catalog


def seed() -> None:
    init_db()
    chapters = load_catalog()
    with SessionLocal() as db:
        for chapter_data in chapters:
            chapter = db.get(Chapter, chapter_data["chapter_id"])
            if chapter is None:
                chapter = Chapter(
                    chapter_id=chapter_data["chapter_id"],
                    schema_version=chapter_data["schema_version"],
                    grade=chapter_data["grade"],
                    chapter_name=chapter_data["chapter_name"],
                    chapter_url=chapter_data["chapter_url"],
                    difficulty=chapter_data["difficulty"],
                    expected_completion_time=chapter_data["expected_completion_time"],
                    prerequisites=chapter_data["prerequisites"],
                )
                db.add(chapter)
            else:
                chapter.schema_version = chapter_data["schema_version"]
                chapter.grade = chapter_data["grade"]
                chapter.chapter_name = chapter_data["chapter_name"]
                chapter.chapter_url = chapter_data["chapter_url"]
                chapter.difficulty = chapter_data["difficulty"]
                chapter.expected_completion_time = chapter_data["expected_completion_time"]
                chapter.prerequisites = chapter_data["prerequisites"]

            existing_subtopics = {subtopic.subtopic_id: subtopic for subtopic in chapter.subtopics}
            for subtopic_data in chapter_data["subtopics"]:
                subtopic = existing_subtopics.get(subtopic_data["subtopic_id"])
                if subtopic is None:
                    db.add(
                        Subtopic(
                            subtopic_id=subtopic_data["subtopic_id"],
                            chapter_id=chapter_data["chapter_id"],
                            name=subtopic_data["name"],
                            difficulty=subtopic_data["difficulty"],
                        )
                    )
                else:
                    subtopic.name = subtopic_data["name"]
                    subtopic.difficulty = subtopic_data["difficulty"]

        db.commit()
    print("Seed data loaded successfully.")


if __name__ == "__main__":
    seed()
