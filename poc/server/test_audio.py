"""音声入力でGemini Live APIをテスト"""
import asyncio
import os
import wave
import struct
from dotenv import load_dotenv

load_dotenv()

from google import genai

async def test_audio_input():
    """音声データを送信してテスト"""
    print("=== Gemini Live API 音声テスト ===")

    client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
    model = "gemini-2.5-flash-native-audio-preview-12-2025"

    # テスト用の無音PCMデータ（1秒分、16kHz、16bit mono）
    silence_samples = [0] * 16000
    silence_pcm = struct.pack('<' + 'h' * len(silence_samples), *silence_samples)

    print(f"Model: {model}")
    print(f"Test audio: {len(silence_pcm)} bytes of silence")

    try:
        config = {
            "response_modalities": ["AUDIO"],
        }

        async with client.aio.live.connect(model=model, config=config) as session:
            print("✅ 接続成功!")

            # 音声データを送信
            print("音声データ送信中...")
            await session.send_realtime_input(
                audio={"data": silence_pcm, "mime_type": "audio/pcm;rate=16000"}
            )

            # 少し待ってからテキストで質問
            await asyncio.sleep(0.5)
            print("テキストメッセージ送信...")
            await session.send_client_content(
                turns={"role": "user", "parts": [{"text": "今、無音の音声を送りました。聞こえましたか？"}]},
                turn_complete=True
            )

            # レスポンスを受信
            print("レスポンス待機中...")
            async for response in session.receive():
                if response.server_content:
                    if response.server_content.model_turn:
                        for part in response.server_content.model_turn.parts:
                            if hasattr(part, 'text') and part.text:
                                print(f"テキスト: {part.text[:100]}...")
                            if hasattr(part, 'inline_data') and part.inline_data:
                                print(f"音声: {len(part.inline_data.data)} bytes")
                    if response.server_content.turn_complete:
                        print("ターン完了")
                        break

    except Exception as e:
        print(f"❌ エラー: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_audio_input())
