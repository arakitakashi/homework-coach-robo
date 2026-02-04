# Auto-Format Hooks Rule

**このルールは、PostToolUse hookによる自動フォーマットとの共存方法を定義します。**

---

## 背景

このプロジェクトでは、`PostToolUse` hookでRuff（Python）やBiome（TypeScript）による自動フォーマットが実行されます。これにより、ツール使用後に以下が自動的に行われます：

- 未使用インポートの削除
- インポートのソート
- コードフォーマット

---

## 問題となるパターン

### ❌ 段階的なインポート追加

```python
# Step 1: Editツールでインポートを追加
from app.models import User  # ← 追加

# Step 2: auto-formatが実行される
# → Userが未使用なのでインポートが削除される！

# Step 3: Editツールで使用コードを追加
user = User()  # ← ImportError発生
```

### ❌ テストファイルの段階的作成

```python
# Step 1: Editツールでテストクラスを追加（インポートなし）
class TestUser:
    def test_create(self):
        user = User()  # ← NameError

# Step 2: Editツールでインポートを追加しようとする
# → すでにエラー状態
```

---

## 推奨パターン

### ✅ Writeツールで全体を一度に書き込む

新しいファイルを作成する場合や、大きな変更を行う場合は、**Writeツールで全体を一度に書き込む**。

```python
# Writeツールで以下を一度に書き込む
"""テストモジュール"""

from app.models import User  # インポートと
from app.services import UserService


class TestUser:
    def test_create(self):
        user = User()  # 使用コードを同時に
        assert user is not None
```

### ✅ インポートと使用コードを同じEditで追加

小さな変更の場合は、**インポートと使用コードを同じEdit操作で追加**。

```python
# 1回のEditで以下を追加
from app.models import User

def create_user():
    return User()
```

### ✅ 既存のインポートブロックに追加する場合

既存ファイルにインポートを追加する場合は、**使用コードも同時に追加**。

---

## ファイル作成のベストプラクティス

### テストファイル作成時

1. **Writeツールを使用**してファイル全体を一度に作成
2. インポート、フィクスチャ、テストクラスをすべて含める
3. 段階的なEdit追加は避ける

### 実装ファイル作成時

1. 新規ファイルは**Writeツール**で作成
2. 既存ファイルへの追加は、インポートと使用コードを**同じEdit**で

---

## `# noqa`コメントの使用

将来使用予定の引数やインポートを残す場合：

```python
def create_session(
    problem: str,
    child_grade: int,  # noqa: ARG002 - 将来のフェーズで使用予定
) -> str:
    pass
```

**注意**:
- 理由を必ずコメントに明記する
- 乱用は避け、本当に必要な場合のみ使用

---

## Claude Codeへの指示

Claude Code（あなた）は、以下を**必ず**実行すること：

1. **新規ファイル作成時はWriteツールを使用**
2. **インポート追加時は使用コードも同時に追加**
3. **テストファイルは全体を一度に書き込む**
4. **段階的なEdit追加でインポートだけを追加しない**

**「まず構造を作って、後でインポートを追加」というアプローチは避けること。**
