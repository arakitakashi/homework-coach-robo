"""Gemini Live API接続テスト"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from google import genai

async def test_live_connection():
    """Live APIへの接続をテスト"""
    print("=== Gemini Live API 接続テスト ===")
    print(f"API Key: {os.getenv('GOOGLE_API_KEY', 'NOT SET')[:10]}...")
    print(f"Use Vertex AI: {os.getenv('GOOGLE_GENAI_USE_VERTEXAI', 'FALSE')}")

    # クライアント初期化
    client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

    model = "gemini-2.5-flash-native-audio-latest"  # AI Studio用最新モデル
    print(f"Model: {model}")

    try:
        # Live API接続
        config = {
            "response_modalities": ["AUDIO"],
        }

        async with client.aio.live.connect(model=model, config=config) as session:
            print("✅ 接続成功!")

            # テキストメッセージを送信
            await session.send_client_content(
                turns={"role": "user", "parts": [{"text": "こんにちは"}]},
                turn_complete=True
            )
            print("メッセージ送信完了")

            # レスポンスを受信
            async for response in session.receive():
                print(f"レスポンス: {response}")
                if response.server_content and response.server_content.turn_complete:
                    break

    except Exception as e:
        print(f"❌ エラー: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_live_connection())
