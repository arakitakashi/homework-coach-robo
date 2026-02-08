"""Initialize RAG Corpus and index sample data.

Usage:
    uv run python scripts/initialize_rag_corpus.py --env dev
"""

import argparse
import asyncio
import logging
import os

from app.services.adk.rag import RagCorpusService, RagDocument

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_sample_data() -> list[RagDocument]:
    """Load sample learning data for initial indexing.

    Returns:
        List of sample RagDocuments
    """
    return [
        # Dialogue history samples
        RagDocument(
            document_id="sample-dialogue-1",
            content="繰り上がりの足し算で23 + 45を一緒に解いた。最初は難しかったけど、一の位から順番に計算することを理解した。",
            metadata={
                "category": "dialogue",
                "subject": "math",
                "grade": 2,
                "problem_type": "addition_carry",
                "timestamp": "2026-02-01T10:00:00Z",
            },
        ),
        RagDocument(
            document_id="sample-dialogue-2",
            content="九九の7の段を練習した。リズムで覚える方法を試したら、すぐに覚えられた。",
            metadata={
                "category": "dialogue",
                "subject": "math",
                "grade": 2,
                "problem_type": "multiplication",
                "timestamp": "2026-02-02T14:00:00Z",
            },
        ),
        # Weak areas samples
        RagDocument(
            document_id="sample-weak-1",
            content="繰り下がりの引き算で3回つまずいた。10の位から借りてくることを忘れやすい。",
            metadata={
                "category": "weak_area",
                "subject": "math",
                "grade": 2,
                "problem_type": "subtraction_borrow",
                "difficulty": 3,
            },
        ),
        RagDocument(
            document_id="sample-weak-2",
            content="文章題で何を求められているかを読み取るのが苦手。問題文を読み飛ばしてしまう傾向がある。",
            metadata={
                "category": "weak_area",
                "subject": "math",
                "grade": 2,
                "problem_type": "word_problem",
                "difficulty": 4,
            },
        ),
        # Success stories samples
        RagDocument(
            document_id="sample-success-1",
            content="ヒントなしで自力で解けた！35 - 18 = 17を繰り下がりに気をつけて正確に計算できた。",
            metadata={
                "category": "success",
                "subject": "math",
                "grade": 2,
                "problem_type": "subtraction_borrow",
                "outcome": "self_solved",
                "points_earned": 3,
            },
        ),
        RagDocument(
            document_id="sample-success-2",
            content="前回は苦手だった九九の8の段を、今日は全問正解できた！成長を実感。",
            metadata={
                "category": "success",
                "subject": "math",
                "grade": 2,
                "problem_type": "multiplication",
                "outcome": "self_solved",
                "points_earned": 3,
            },
        ),
        # Curriculum samples
        RagDocument(
            document_id="sample-curriculum-1",
            content="2年生の算数：繰り上がり・繰り下がりのある足し算引き算（2桁）。学習目標：筆算の方法を理解し、正確に計算できる。",
            metadata={
                "category": "curriculum",
                "subject": "math",
                "grade": 2,
                "topic": "addition_subtraction_2digit",
            },
        ),
        RagDocument(
            document_id="sample-curriculum-2",
            content="2年生の算数：九九の暗記と応用。学習目標：1の段から9の段まですべて暗記し、文章題に応用できる。",
            metadata={
                "category": "curriculum",
                "subject": "math",
                "grade": 2,
                "topic": "multiplication_table",
            },
        ),
    ]


async def main(env: str) -> None:
    """Initialize RAG Corpus and index sample data.

    Args:
        env: Environment (dev, staging, prod)
    """
    # Get project configuration
    project_id = os.getenv("GCP_PROJECT_ID", f"homework-coach-{env}")
    location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    corpus_name = os.getenv("RAG_CORPUS_NAME", "homework-coach-memory-store")

    logger.info(
        f"Initializing RAG Corpus for environment: {env}",
        extra={
            "project_id": project_id,
            "location": location,
            "corpus_name": corpus_name,
        },
    )

    # Initialize services
    corpus_service = RagCorpusService(project_id=project_id, location=location)

    try:
        # Step 1: Create RAG Corpus
        logger.info("Creating RAG Corpus...")
        full_corpus_name = await corpus_service.create_corpus(
            corpus_name=corpus_name,
            description="宿題コーチロボット - 学習履歴・苦手分野・成功体験の記憶",
        )
        logger.info(f"✅ Corpus created: {full_corpus_name}")

    except Exception as e:
        if "already exists" in str(e).lower():
            logger.warning("Corpus already exists, continuing with indexing...")
        else:
            logger.error(f"Failed to create corpus: {e}")
            raise

    # Step 2: Index sample data
    logger.info("Loading sample data...")
    sample_documents = load_sample_data()
    logger.info(f"Loaded {len(sample_documents)} sample documents")

    logger.info("Indexing sample data...")
    try:
        indexed_ids = await corpus_service.index_documents_batch(
            corpus_name=corpus_name,
            documents=sample_documents,
        )
        logger.info(f"✅ Indexed {len(indexed_ids)} documents")

        # Print summary by category
        categories: dict[str, int] = {}
        for doc in sample_documents:
            category = doc.metadata.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1

        logger.info("Indexing summary:")
        for category, count in categories.items():
            logger.info(f"  - {category}: {count} documents")

    except Exception as e:
        logger.error(f"Failed to index sample data: {e}")
        raise

    logger.info("🎉 RAG Corpus initialization complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize RAG Corpus")
    parser.add_argument(
        "--env",
        type=str,
        default="dev",
        choices=["dev", "staging", "prod"],
        help="Environment to initialize",
    )

    args = parser.parse_args()
    asyncio.run(main(args.env))
