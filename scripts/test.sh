#!/bin/bash
# テスト実行スクリプト

set -e

echo "🧪 テストを実行中..."
echo ""

# フロントエンドテスト
echo "📦 フロントエンドテスト..."
cd frontend
bun run test --run
cd ..

echo ""

# バックエンドテスト
echo "🐍 バックエンドテスト..."
cd backend
uv run pytest -v
cd ..

echo ""
echo "✅ すべてのテストが完了しました"
