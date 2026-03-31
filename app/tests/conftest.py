from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_session
from app.main import create_app
from app.models import Chapter, Subtopic
from app.models.base import Base


@pytest.fixture
def session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with TestingSessionLocal() as db:
        db.add_all(
            [
                Chapter(
                    chapter_id="grade6_fractions",
                    schema_version="1.0",
                    grade=6,
                    chapter_name="Fractions",
                    chapter_url="/grade6/fractions",
                    difficulty=0.35,
                    expected_completion_time=780,
                    prerequisites=[],
                ),
                Chapter(
                    chapter_id="grade7_algebraic_expressions",
                    schema_version="1.0",
                    grade=7,
                    chapter_name="Algebraic Expressions",
                    chapter_url="/grade7/algebraic-expressions",
                    difficulty=0.58,
                    expected_completion_time=960,
                    prerequisites=["grade6_fractions", "grade7_ratio_and_proportion"],
                ),
                Chapter(
                    chapter_id="grade7_ratio_and_proportion",
                    schema_version="1.0",
                    grade=7,
                    chapter_name="Ratio and Proportion",
                    chapter_url="/grade7/ratio-and-proportion",
                    difficulty=0.50,
                    expected_completion_time=900,
                    prerequisites=["grade6_fractions"],
                ),
                Chapter(
                    chapter_id="grade8_linear_equations",
                    schema_version="1.0",
                    grade=8,
                    chapter_name="Linear Equations",
                    chapter_url="/grade8/linear-equations",
                    difficulty=0.74,
                    expected_completion_time=1200,
                    prerequisites=[
                        "grade7_algebraic_expressions",
                        "grade7_ratio_and_proportion",
                    ],
                ),
                Subtopic(
                    subtopic_id="grade7_ratio_and_proportion__simplifying_ratios",
                    chapter_id="grade7_ratio_and_proportion",
                    name="Simplifying Ratios",
                    difficulty=0.44,
                ),
                Subtopic(
                    subtopic_id="grade7_ratio_and_proportion__word_problems",
                    chapter_id="grade7_ratio_and_proportion",
                    name="Ratio Word Problems",
                    difficulty=0.56,
                ),
                Subtopic(
                    subtopic_id="grade8_linear_equations__solving_one_step_equations",
                    chapter_id="grade8_linear_equations",
                    name="Solving One-Step Equations",
                    difficulty=0.62,
                ),
                Subtopic(
                    subtopic_id="grade8_linear_equations__solving_multi_step_equations",
                    chapter_id="grade8_linear_equations",
                    name="Solving Multi-Step Equations",
                    difficulty=0.82,
                ),
            ]
        )
        db.commit()
        yield db


@pytest.fixture
def client(session: Session) -> TestClient:
    app = create_app()

    def override_get_session():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
