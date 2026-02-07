"""音声ストリームスキーマのテスト"""

from app.schemas.voice_stream import (
    ADKContentPart,
    ADKEventMessage,
    ADKInlineData,
    ADKTranscription,
    TextInputMessage,
)


class TestADKTranscription:
    """ADKTranscriptionモデルのテスト"""

    def test_create_with_text_and_finished(self) -> None:
        """テキストとfinishedフラグで作成できる"""
        transcription = ADKTranscription(text="こんにちは", finished=True)
        assert transcription.text == "こんにちは"
        assert transcription.finished is True

    def test_create_with_partial(self) -> None:
        """部分的なトランスクリプションを作成できる"""
        transcription = ADKTranscription(text="こん", finished=False)
        assert transcription.text == "こん"
        assert transcription.finished is False

    def test_serialization(self) -> None:
        """JSON形式にシリアライズできる"""
        transcription = ADKTranscription(text="テスト", finished=True)
        data = transcription.model_dump()
        assert data == {"text": "テスト", "finished": True}


class TestADKInlineData:
    """ADKInlineDataモデルのテスト"""

    def test_create_with_audio(self) -> None:
        """音声データで作成できる"""
        inline_data = ADKInlineData(mimeType="audio/pcm", data="base64data")
        assert inline_data.mimeType == "audio/pcm"
        assert inline_data.data == "base64data"

    def test_serialization(self) -> None:
        """JSON形式にシリアライズできる"""
        inline_data = ADKInlineData(mimeType="audio/pcm", data="abc123")
        data = inline_data.model_dump()
        assert data == {"mimeType": "audio/pcm", "data": "abc123"}


class TestADKContentPart:
    """ADKContentPartモデルのテスト"""

    def test_create_with_text(self) -> None:
        """テキストパートを作成できる"""
        part = ADKContentPart(text="テスト")
        assert part.text == "テスト"
        assert part.inlineData is None

    def test_create_with_inline_data(self) -> None:
        """インラインデータパートを作成できる"""
        inline = ADKInlineData(mimeType="audio/pcm", data="base64")
        part = ADKContentPart(inlineData=inline)
        assert part.text is None
        assert part.inlineData is not None
        assert part.inlineData.mimeType == "audio/pcm"

    def test_serialization_excludes_none(self) -> None:
        """Noneフィールドはシリアライズで除外される"""
        part = ADKContentPart(text="テスト")
        data = part.model_dump(exclude_none=True)
        assert data == {"text": "テスト"}
        assert "inlineData" not in data


class TestADKEventMessage:
    """ADKEventMessageモデルのテスト"""

    def test_create_minimal(self) -> None:
        """最小構成で作成できる"""
        event = ADKEventMessage()
        assert event.author is None
        assert event.turnComplete is None
        assert event.interrupted is None
        assert event.inputTranscription is None
        assert event.outputTranscription is None
        assert event.content is None

    def test_create_turn_complete(self) -> None:
        """ターン完了イベントを作成できる"""
        event = ADKEventMessage(author="agent", turnComplete=True)
        assert event.author == "agent"
        assert event.turnComplete is True

    def test_create_interrupted(self) -> None:
        """中断イベントを作成できる"""
        event = ADKEventMessage(interrupted=True)
        assert event.interrupted is True

    def test_create_with_transcription(self) -> None:
        """トランスクリプション付きイベントを作成できる"""
        input_t = ADKTranscription(text="ユーザー音声", finished=True)
        output_t = ADKTranscription(text="AI応答", finished=False)
        event = ADKEventMessage(
            inputTranscription=input_t,
            outputTranscription=output_t,
        )
        assert event.inputTranscription is not None
        assert event.inputTranscription.text == "ユーザー音声"
        assert event.outputTranscription is not None
        assert event.outputTranscription.text == "AI応答"

    def test_create_with_audio_content(self) -> None:
        """音声コンテンツ付きイベントを作成できる"""
        inline = ADKInlineData(mimeType="audio/pcm", data="base64audio")
        part = ADKContentPart(inlineData=inline)
        event = ADKEventMessage(
            author="agent",
            content={"parts": [part]},
        )
        assert event.content is not None
        assert len(event.content["parts"]) == 1

    def test_serialization_camel_case(self) -> None:
        """camelCaseでシリアライズされる（by_alias）"""
        event = ADKEventMessage(
            author="agent",
            turnComplete=True,
        )
        data = event.model_dump(exclude_none=True, by_alias=True)
        assert "turnComplete" in data
        assert "author" in data

    def test_to_json_string(self) -> None:
        """JSON文字列に変換できる"""
        event = ADKEventMessage(turnComplete=True)
        json_str = event.model_dump_json(exclude_none=True, by_alias=True)
        assert '"turnComplete":true' in json_str


class TestTextInputMessage:
    """TextInputMessageモデルのテスト"""

    def test_create(self) -> None:
        """テキスト入力メッセージを作成できる"""
        msg = TextInputMessage(type="text", text="こんにちは")
        assert msg.type == "text"
        assert msg.text == "こんにちは"

    def test_type_is_literal_text(self) -> None:
        """typeフィールドは'text'のみ"""
        msg = TextInputMessage(type="text", text="テスト")
        assert msg.type == "text"

    def test_serialization(self) -> None:
        """JSON形式にシリアライズできる"""
        msg = TextInputMessage(type="text", text="テスト")
        data = msg.model_dump()
        assert data == {"type": "text", "text": "テスト"}
