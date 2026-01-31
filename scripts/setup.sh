#!/bin/bash
# プロジェクトセットアップスクリプト

set -e

echo "🚀 宿題コーチロボット - プロジェクトセットアップ"
echo "================================================"

# フロントエンドセットアップ
echo ""
echo "📦 フロントエンドの依存関係をインストール中..."
cd frontend
bun install
cd ..

# バックエンドセットアップ
echo ""
echo "🐍 バックエンドの依存関係をインストール中..."
cd backend
uv sync --all-extras
cd ..

echo ""
echo "✅ セットアップ完了！"
echo ""
echo "開発サーバーを起動するには:"
echo "  ./scripts/dev.sh"
