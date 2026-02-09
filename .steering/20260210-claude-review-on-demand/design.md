# Design - Claude Code Review オンデマンド化

## 変更対象

`.github/workflows/claude-code-review.yml` のみ

## 変更内容

### Before
```yaml
on:
  pull_request:
    types: [opened, synchronize, ready_for_review, reopened]
```

### After
```yaml
on:
  pull_request:
    types: [labeled]
```

- `labeled` イベントで `claude-review` ラベルが付与された時のみ実行
- job レベルで `if: github.event.label.name == 'claude-review'` 条件を追加
