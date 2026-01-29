# Cloud Firestore 設計ドキュメント

**Document Version**: 1.0
**Last Updated**: 2026-01-28
**Status**: 設計完了

---

## 1. Cloud Firestoreに保存するデータ

### 1.1 リアルタイムデータの定義

**リアルタイムデータ** = セッション進行中に頻繁に更新され、即座に参照が必要なデータ

以下のデータをCloud Firestoreに保存します：

---

### 1.2 具体的なデータ種別

#### A. セッション状態データ（最重要）

**保存データ:**
```typescript
sessions/{session_id}
  ├─ id: string
  ├─ userId: string
  ├─ appName: string
  ├─ createdAt: timestamp
  ├─ updatedAt: timestamp        // リアルタイム更新
  ├─ isActive: boolean            // セッション進行中かどうか
  ├─ currentProblemId: string     // 現在取り組んでいる問題
  ├─ currentProblemStartTime: timestamp
  ├─ hintLevel: number            // 現在のヒントレベル（0-3）
  ├─ attemptsCount: number        // 現在の問題の試行回数
  ├─ emotionalState: string       // 現在の感情状態
  └─ lastActivityTime: timestamp  // 最終活動時刻
```

**更新頻度:** 秒単位（音声対話中）

**用途:**
- WebSocketセッションの復旧
- 対話状態の永続化
- 複数デバイス間での同期
- セッション再開機能

#### B. ユーザープロフィール

**保存データ:**
```typescript
users/{user_id}
  ├─ id: string
  ├─ name: string
  ├─ gradeLevel: number (1-3)
  ├─ createdAt: timestamp
  ├─ updatedAt: timestamp
  ├─ settings: map                // リアルタイム更新可能
  │   ├─ preferredCharacter: string
  │   ├─ voiceSpeed: number
  │   ├─ volumeLevel: number
  │   └─ parentEmail: string
  ├─ stats: map                   // キャッシュされた統計（リアルタイム更新）
  │   ├─ totalPoints: number
  │   ├─ problemsSolved: number
  │   ├─ selfDiscoveryCount: number
  │   └─ lastSessionAt: timestamp
  └─ currentSessionId: string     // 現在アクティブなセッション
```

**更新頻度:** 分単位〜時間単位

**用途:**
- ユーザー設定の即時反映
- プロフィール情報の取得
- リアルタイム統計の表示
- 保護者ダッシュボードへの同期

#### C. 問題バンク

**保存データ:**
```typescript
problems/{problem_id}
  ├─ id: string
  ├─ subject: string ('math' | 'japanese')
  ├─ gradeLevel: number (1-3)
  ├─ difficulty: number (1-5)
  ├─ questionText: string
  ├─ correctAnswer: string
  ├─ relatedConcepts: array<string>
  ├─ commonMistakes: array<string>
  ├─ hints: map
  │   ├─ level1: array<string>
  │   ├─ level2: array<string>
  │   └─ level3: array<string>
  ├─ usageStats: map              // リアルタイム更新
  │   ├─ totalAttempts: number
  │   ├─ successRate: number
  │   └─ averageHintsUsed: number
  └─ updatedAt: timestamp
```

**更新頻度:** 低（問題自体はほぼ静的、統計のみ更新）

**用途:**
- 問題の即時取得
- ヒント情報の動的取得
- 問題統計のリアルタイム更新

#### D. 進行中の対話履歴（一時的）

**保存データ:**
```typescript
sessions/{session_id}/dialogue_turns/{turn_id}
  ├─ turnId: string
  ├─ speaker: string ('child' | 'coach')
  ├─ timestamp: timestamp
  ├─ transcript: string
  ├─ emotion: string
  ├─ questionType: string
  └─ audioUrl: string (optional)
```

**更新頻度:** 秒単位（対話ごと）

**用途:**
- 対話コンテキストの保持
- セッション中断・再開時の復元
- リアルタイムな対話履歴表示

**重要:** セッション終了時にBigQueryに移行し、Firestoreからは削除

#### E. 保護者向けリアルタイム通知

**保存データ:**
```typescript
users/{parent_user_id}/notifications/{notification_id}
  ├─ id: string
  ├─ childUserId: string
  ├─ type: string ('session_started' | 'milestone_achieved' | 'session_completed')
  ├─ message: string
  ├─ createdAt: timestamp
  ├─ read: boolean
  └─ metadata: map
```

**更新頻度:** イベント駆動（セッション開始/終了時など）

**用途:**
- 保護者への即時通知
- 子供の学習状況のリアルタイム共有
- プッシュ通知のトリガー

---

## 2. なぜCloud Firestoreを選択したか

### 2.1 比較対象データベース

- **Cloud Firestore** ✅ 採用
- PostgreSQL（Cloud SQL）
- Cloud Spanner
- MongoDB（Atlas）
- Redis（Memorystore）

---

### 2.2 Cloud Firestoreの選択理由

#### 理由1: リアルタイム同期機能

**Firestoreの強み:**
```javascript
// クライアントサイドでリアルタイムリスナー
const sessionRef = doc(db, 'sessions', sessionId);
onSnapshot(sessionRef, (snapshot) => {
  const data = snapshot.data();
  // データ変更時に自動的にUIを更新
  updateUI(data);
});
```

**メリット:**
- データ変更が即座にクライアントに反映
- WebSocketやPollingの実装不要
- サーバーサイドのコード削減

**代替案との比較:**
- PostgreSQL: リアルタイム同期機能なし（自前でWebSocket実装が必要）
- MongoDB: Change Streamsはあるがサーバーサイド処理が必要

#### 理由2: Firebase Authenticationとの統合

**Firestoreの強み:**
```javascript
// Firebase Authと完全統合
const user = auth.currentUser;
const userRef = doc(db, 'users', user.uid);

// セキュリティルールでユーザー認証
// firestore.rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

**メリット:**
- ユーザー認証と権限管理が簡単
- クライアントから直接アクセス可能（セキュリティルール適用）
- サーバーサイドのAPIエンドポイント実装が不要

**代替案との比較:**
- PostgreSQL: 別途認証・認可ロジックが必要
- MongoDB: Firebase Auth統合には追加実装が必要

#### 理由3: スケーラビリティ

**Firestoreの強み:**
- 自動シャーディング
- 自動スケーリング
- 管理不要（サーバーレス）

**データ規模:**
- ドキュメント数: 無制限
- 読み込み: 100万/秒（自動スケール）
- 書き込み: 10,000/秒/ドキュメント

**代替案との比較:**
- Cloud SQL（PostgreSQL）: 垂直スケーリングのみ、手動管理必要
- Cloud Spanner: 高コスト（月$1,000〜）

#### 理由4: オフラインサポート

**Firestoreの強み:**
```javascript
// オフライン永続化
enableIndexedDbPersistence(db).catch((err) => {
  if (err.code === 'failed-precondition') {
    // 複数タブで開いている
  } else if (err.code === 'unimplemented') {
    // ブラウザ非対応
  }
});
```

**メリット:**
- ネットワーク切断時もローカルキャッシュから読み込み
- オフラインでの書き込みを自動で同期
- 低学年児童が不安定なWi-Fi環境でも使える

**代替案との比較:**
- PostgreSQL: オフラインサポートなし
- MongoDB: サーバーサイドでの実装が必要

#### 理由5: クエリの柔軟性とインデックス

**Firestoreの強み:**
```javascript
// 複合クエリ
const q = query(
  collection(db, 'sessions'),
  where('userId', '==', userId),
  where('isActive', '==', true),
  orderBy('createdAt', 'desc'),
  limit(10)
);
```

**メリット:**
- 複合インデックスの自動提案
- インデックス作成が簡単
- 柔軟なクエリ（範囲、並び替え、制限）

**代替案との比較:**
- Redis: クエリ機能が限定的（キーバリューストア）
- PostgreSQL: クエリは柔軟だが、リアルタイム同期なし

#### 理由6: コスト効率

**Firestore料金（2026年1月）:**
```
無料枠（毎日）:
- 読み込み: 50,000
- 書き込み: 20,000
- 削除: 20,000
- ストレージ: 1GB

超過料金:
- 読み込み: $0.06/10万
- 書き込み: $0.18/10万
- 削除: $0.02/10万
- ストレージ: $0.18/GB/月
```

**本プロジェクトの試算（月1,000セッション）:**
```
読み込み: 100万回 → $0.60
書き込み: 50万回 → $0.90
削除: 5万回 → $0.01
ストレージ: 5GB → $0.90
合計: 約$2.50/月
```

**代替案との比較:**
- Cloud SQL（db-f1-micro）: $7/月〜（最小構成）
- Cloud Spanner: $1,000/月〜（最小3ノード）
- MongoDB Atlas: $57/月〜（M10クラスター）

#### 理由7: ADKとの統合

**FirestoreSessionServiceの実装:**
```python
from google.adk.sessions import SessionService
from google.cloud import firestore

class FirestoreSessionService(SessionService):
    def __init__(self):
        self.db = firestore.AsyncClient()

    async def get_session(self, app_name: str, user_id: str, session_id: str):
        doc_ref = self.db.collection('sessions').document(session_id)
        doc = await doc_ref.get()
        return Session.from_dict(doc.to_dict()) if doc.exists else None
```

**メリット:**
- ADKのSessionServiceインターフェースに容易に適合
- 非同期操作のサポート
- Google Cloud SDKとの統合

---

### 2.3 Firestoreの制約と対処法

#### 制約1: 1秒あたりの書き込み制限

**制約:** 1つのドキュメントに対して1秒あたり1回の書き込み

**対処法:**
```javascript
// サブコレクションで分散
sessions/{session_id}/dialogue_turns/{turn_id}  // 各ターンは別ドキュメント
```

#### 制約2: クエリの制限

**制約:** 範囲フィルタは1つのフィールドのみ

**対処法:**
```javascript
// 複合インデックスを作成
// firestore.indexes.json
{
  "indexes": [
    {
      "collectionGroup": "sessions",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "userId", "order": "ASCENDING" },
        { "fieldPath": "createdAt", "order": "DESCENDING" }
      ]
    }
  ]
}
```

#### 制約3: トランザクションの制限

**制約:** トランザクションは最大500ドキュメント

**対処法:**
```python
# バッチ処理を使用
batch = db.batch()
for doc_ref in doc_refs[:500]:  # 500ドキュメントずつ処理
    batch.update(doc_ref, {...})
await batch.commit()
```

---

### 2.4 FirestoreとBigQueryの役割分担

| データ種別 | Firestore | BigQuery | 理由 |
|-----------|-----------|----------|------|
| **セッション状態** | ✅ メイン | ❌ | リアルタイム更新が必要 |
| **ユーザープロフィール** | ✅ メイン | ❌ | 即時参照が必要 |
| **進行中の対話** | ✅ 一時保存 | ✅ 永久保存 | セッション中はFirestore、終了後にBigQuery |
| **完了した対話履歴** | ❌ | ✅ メイン | 分析用、リアルタイム不要 |
| **学習統計・集計** | ✅ キャッシュ | ✅ ソース | BigQueryで集計→Firestoreにキャッシュ |
| **問題バンク** | ✅ メイン | ❌ | 即時参照が必要 |

**データフロー:**
```
セッション開始
  ↓
Firestoreにセッション作成
  ↓
対話進行中（Firestoreにリアルタイム保存）
  ↓
セッション終了
  ↓
BigQueryに全データ永久保存
  ↓
Firestoreから対話履歴削除（セッション状態のみ保持）
```

---

### 2.5 Redisとの役割分担

| データ種別 | Firestore | Redis | 理由 |
|-----------|-----------|-------|------|
| **セッション状態** | ✅ メイン | ❌ | 永続化が必要 |
| **TTS音声キャッシュ** | ❌ | ✅ | 一時的、高速アクセス |
| **よく使うフレーズ** | ❌ | ✅ | 一時的、高速アクセス |
| **レート制限カウンター** | ❌ | ✅ | TTL機能が便利 |

---

## 3. Firestoreデータモデル詳細

### 3.1 コレクション構造

```
/users
  /{user_id}
    - プロフィール情報
    - 設定
    - 統計キャッシュ

    /notifications
      /{notification_id}
        - 保護者向け通知

/sessions
  /{session_id}
    - セッション状態
    - 現在の問題
    - 感情状態

    /dialogue_turns (サブコレクション)
      /{turn_id}
        - 対話ターンごとのデータ

/problems
  /{problem_id}
    - 問題データ
    - ヒント
    - 統計
```

### 3.2 セキュリティルール

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // ユーザーは自分のデータのみアクセス可能
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;

      // 保護者は子供のデータを読み取り可能
      match /notifications/{notificationId} {
        allow read: if request.auth != null &&
          (request.auth.uid == userId || isParentOf(userId));
      }
    }

    // セッションは所有者のみアクセス可能
    match /sessions/{sessionId} {
      allow read, write: if request.auth != null &&
        request.auth.uid == resource.data.userId;

      match /dialogue_turns/{turnId} {
        allow read, write: if request.auth != null &&
          request.auth.uid == get(/databases/$(database)/documents/sessions/$(sessionId)).data.userId;
      }
    }

    // 問題は全員が読み取り可能、書き込みは管理者のみ
    match /problems/{problemId} {
      allow read: if request.auth != null;
      allow write: if request.auth.token.admin == true;
    }

    // ヘルパー関数
    function isParentOf(childUserId) {
      return get(/databases/$(database)/documents/users/$(childUserId)).data.parentEmail == request.auth.token.email;
    }
  }
}
```

---

## 4. まとめ

### Cloud Firestoreを選択した主な理由

1. **リアルタイム同期** - セッション状態の即時反映
2. **Firebase Auth統合** - 認証・認可が簡単
3. **オフラインサポート** - 不安定なネットワークでも動作
4. **スケーラビリティ** - 管理不要の自動スケーリング
5. **コスト効率** - 小〜中規模では非常に安い
6. **ADK統合** - SessionServiceの実装が容易

### 役割分担

- **Firestore**: リアルタイムデータ（セッション状態、ユーザー情報）
- **BigQuery**: 分析用データ（完了した対話履歴、学習統計）
- **Redis**: 一時キャッシュ（TTS音声、レート制限）

この組み合わせにより、リアルタイム性、分析能力、コスト効率を最大化しています。

---

**作成者**: Claude Code
