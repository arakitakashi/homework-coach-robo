#!/bin/bash
# 開発サーバー起動スクリプト

set -e

echo "🚀 開発サーバーを起動中..."
echo ""

# バックエンドを起動（バックグラウンド）
echo "🐍 バックエンドサーバーを起動中 (http://localhost:8000)..."
cd backend
uv run uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# フロントエンドを起動
echo "⚛️  フロントエンドサーバーを起動中 (http://localhost:3000)..."
cd frontend
bun run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ 開発サーバーが起動しました"
echo "   フロントエンド: http://localhost:3000"
echo "   バックエンド:   http://localhost:8000"
echo "   API docs:       http://localhost:8000/docs"
echo ""
echo "終了するには Ctrl+C を押してください"

# 終了時にプロセスをクリーンアップ
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

# 待機
wait
