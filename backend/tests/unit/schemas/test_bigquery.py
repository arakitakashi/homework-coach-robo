"""BigQuery用Pydanticスキーマのユニットテスト"""

from datetime import datetime, timezone

from app.schemas.bigquery import (
    DialogueSessionBQ,
    DialogueTurnBQ,
    LearningHistoryBQ,
    LearningProfileSnapshotBQ,
    SubjectUnderstandingBQ,
)


class TestDialogueTurnBQ:
    """DialogueTurnBQスキーマのテスト"""

    def test_valid_dialogue_turn(self) -> None:
        """正常な対話ターンの作成"""
        turn = DialogueTurnBQ(
            turn_id=1,
            speaker="user",
            content="1 + 1 = ?",
            timestamp=datetime.now(timezone.utc),
        )
        assert turn.turn_id == 1
        assert turn.speaker == "user"
        assert turn.content == "1 + 1 = ?"
        assert turn.emotion is None

    def test_dialogue_turn_with_emotion(self) -> None:
        """感情情報を含む対話ターン"""
        turn = DialogueTurnBQ(
            turn_id=2,
            speaker="assistant",
            content="いいね！",
            timestamp=datetime.now(timezone.utc),
            emotion="positive",
        )
        assert turn.emotion == "positive"

    def test_dialogue_turn_serialization(self) -> None:
        """JSON形式へのシリアライゼーション"""
        turn = DialogueTurnBQ(
            turn_id=1,
            speaker="user",
            content="test",
            timestamp=datetime(2026, 2, 15, 10, 0, 0, tzinfo=timezone.utc),
        )
        data = turn.model_dump(mode="json")
        assert isinstance(data["timestamp"], str)
        assert data["turn_id"] == 1


class TestDialogueSessionBQ:
    """DialogueSessionBQスキーマのテスト"""

    def test_valid_session(self) -> None:
        """正常なセッションの作成"""
        session = DialogueSessionBQ(
            session_id="session123",
            user_id="user456",
            problem="1 + 1 = ?",
            start_time=datetime.now(timezone.utc),
        )
        assert session.session_id == "session123"
        assert session.user_id == "user456"
        assert session.problem == "1 + 1 = ?"
        assert session.end_time is None
        assert session.dialogue_turns == []
        assert session.total_hints_used == 0
        assert session.self_solved_count == 0
        assert session.total_points == 0

    def test_session_with_dialogue_turns(self) -> None:
        """対話ターンを含むセッション"""
        turns = [
            DialogueTurnBQ(
                turn_id=1,
                speaker="user",
                content="test",
                timestamp=datetime.now(timezone.utc),
            )
        ]
        session = DialogueSessionBQ(
            session_id="session123",
            user_id="user456",
            problem="1 + 1 = ?",
            start_time=datetime.now(timezone.utc),
            dialogue_turns=turns,
        )
        assert len(session.dialogue_turns) == 1
        assert session.dialogue_turns[0].content == "test"

    def test_session_with_metrics(self) -> None:
        """メトリクスを含むセッション"""
        session = DialogueSessionBQ(
            session_id="session123",
            user_id="user456",
            problem="1 + 1 = ?",
            start_time=datetime.now(timezone.utc),
            total_hints_used=3,
            self_solved_count=1,
            total_points=2,
        )
        assert session.total_hints_used == 3
        assert session.self_solved_count == 1
        assert session.total_points == 2

    def test_session_serialization(self) -> None:
        """JSON形式へのシリアライゼーション"""
        session = DialogueSessionBQ(
            session_id="session123",
            user_id="user456",
            problem="1 + 1 = ?",
            start_time=datetime(2026, 2, 15, 10, 0, 0, tzinfo=timezone.utc),
            end_time=datetime(2026, 2, 15, 10, 10, 0, tzinfo=timezone.utc),
        )
        data = session.model_dump(mode="json")
        assert isinstance(data["start_time"], str)
        assert isinstance(data["end_time"], str)
        assert data["session_id"] == "session123"


class TestLearningHistoryBQ:
    """LearningHistoryBQスキーマのテスト"""

    def test_valid_learning_history(self) -> None:
        """正常な学習履歴の作成"""
        history = LearningHistoryBQ(
            id="history123",
            user_id="user456",
            problem_id="problem789",
            subject="math",
            grade_level=2,
            attempted_at=datetime.now(timezone.utc),
            solved_independently=True,
            hints_used=1,
            time_spent_seconds=300,
            points_earned=3,
            session_id="session123",
        )
        assert history.id == "history123"
        assert history.user_id == "user456"
        assert history.problem_id == "problem789"
        assert history.subject == "math"
        assert history.grade_level == 2
        assert history.solved_independently is True
        assert history.hints_used == 1
        assert history.time_spent_seconds == 300
        assert history.points_earned == 3
        assert history.session_id == "session123"

    def test_learning_history_serialization(self) -> None:
        """JSON形式へのシリアライゼーション"""
        history = LearningHistoryBQ(
            id="history123",
            user_id="user456",
            problem_id="problem789",
            subject="math",
            grade_level=2,
            attempted_at=datetime(2026, 2, 15, 10, 0, 0, tzinfo=timezone.utc),
            solved_independently=False,
            hints_used=2,
            time_spent_seconds=600,
            points_earned=1,
            session_id="session123",
        )
        data = history.model_dump(mode="json")
        assert isinstance(data["attempted_at"], str)
        assert data["solved_independently"] is False


class TestSubjectUnderstandingBQ:
    """SubjectUnderstandingBQスキーマのテスト"""

    def test_valid_subject_understanding(self) -> None:
        """正常な科目別理解度の作成"""
        understanding = SubjectUnderstandingBQ(
            subject="math",
            topic="addition",
            level="intermediate",
            trend="improving",
        )
        assert understanding.subject == "math"
        assert understanding.topic == "addition"
        assert understanding.level == "intermediate"
        assert understanding.trend == "improving"

    def test_subject_understanding_serialization(self) -> None:
        """JSON形式へのシリアライゼーション"""
        understanding = SubjectUnderstandingBQ(
            subject="japanese",
            topic="kanji",
            level="beginner",
            trend="stable",
        )
        data = understanding.model_dump(mode="json")
        assert data["subject"] == "japanese"
        assert data["level"] == "beginner"


class TestLearningProfileSnapshotBQ:
    """LearningProfileSnapshotBQスキーマのテスト"""

    def test_valid_profile_snapshot(self) -> None:
        """正常な学習プロファイルスナップショットの作成"""
        snapshot = LearningProfileSnapshotBQ(
            id="snapshot123",
            user_id="user456",
            snapshot_at=datetime.now(timezone.utc),
            persistence_score=0.8,
            independence_score=0.7,
            reflection_quality=0.9,
            hint_dependency=0.3,
        )
        assert snapshot.id == "snapshot123"
        assert snapshot.user_id == "user456"
        assert snapshot.persistence_score == 0.8
        assert snapshot.independence_score == 0.7
        assert snapshot.reflection_quality == 0.9
        assert snapshot.hint_dependency == 0.3
        assert snapshot.subject_understanding == []

    def test_profile_snapshot_with_subject_understanding(self) -> None:
        """科目別理解度を含むプロファイルスナップショット"""
        understanding = [
            SubjectUnderstandingBQ(
                subject="math",
                topic="addition",
                level="intermediate",
                trend="improving",
            )
        ]
        snapshot = LearningProfileSnapshotBQ(
            id="snapshot123",
            user_id="user456",
            snapshot_at=datetime.now(timezone.utc),
            persistence_score=0.8,
            independence_score=0.7,
            reflection_quality=0.9,
            hint_dependency=0.3,
            subject_understanding=understanding,
        )
        assert len(snapshot.subject_understanding) == 1
        assert snapshot.subject_understanding[0].subject == "math"

    def test_profile_snapshot_serialization(self) -> None:
        """JSON形式へのシリアライゼーション"""
        understanding = [
            SubjectUnderstandingBQ(
                subject="math",
                topic="addition",
                level="intermediate",
                trend="improving",
            )
        ]
        snapshot = LearningProfileSnapshotBQ(
            id="snapshot123",
            user_id="user456",
            snapshot_at=datetime(2026, 2, 15, 10, 0, 0, tzinfo=timezone.utc),
            persistence_score=0.8,
            independence_score=0.7,
            reflection_quality=0.9,
            hint_dependency=0.3,
            subject_understanding=understanding,
        )
        data = snapshot.model_dump(mode="json")
        assert isinstance(data["snapshot_at"], str)
        assert len(data["subject_understanding"]) == 1
        assert data["subject_understanding"][0]["subject"] == "math"
