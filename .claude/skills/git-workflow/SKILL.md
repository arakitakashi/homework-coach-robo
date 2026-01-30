# Git Workflow - Git Flow + Conventional Commits

**Version**: 1.0 | **Last Updated**: 2026-01-31 | **For**: Git Flow + Conventional Commits

---

## Overview

Git Flow branching strategy with Conventional Commits format.

**Key Principles:**
- Git Flow (main/develop/feature/hotfix)
- Conventional Commits format
- Small, reviewable PRs
- Self-review before submission

---

## Quick Start

### Branch Strategy (Git Flow)

```
main (production)
  ↑
develop (development)
  ↑
feature/xxx (features)
hotfix/xxx (urgent fixes)
```

### Create New Branch

```bash
# Feature
git checkout develop
git pull origin develop
git checkout -b feature/dialogue-engine

# Bug fix
git checkout -b fix/audio-recording-issue

# Hotfix
git checkout main
git checkout -b hotfix/critical-audio-bug

# Refactor
git checkout -b refactor/reorganize-components

# Documentation
git checkout -b docs/update-architecture
```

---

## Branch Naming

### Format

```
<type>/<description>
```

### Types

```bash
# Feature development
feature/dialogue-engine
feature/camera-interface
feature/hint-system-level-1

# Bug fixes
fix/audio-recording-issue
fix/websocket-disconnect

# Hotfixes (production)
hotfix/critical-audio-bug
hotfix/security-vulnerability

# Refactoring
refactor/reorganize-components
refactor/optimize-audio-processing

# Documentation
docs/update-architecture
docs/add-api-documentation
```

---

## Commit Message Format

### Structure

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

```bash
feat:     New feature
fix:      Bug fix
docs:     Documentation
style:    Code formatting (no logic change)
refactor: Code refactoring
test:     Tests
chore:    Build/config changes
perf:     Performance improvement
ci:       CI/CD changes
```

### Examples

```bash
# ✅ Good: Clear and specific
feat(dialogue): add 3-level hint system

Implemented the 3-level hint system:
- Level 1: Problem understanding confirmation
- Level 2: Recall of learned knowledge
- Level 3: Partial support

Closes #42

# ✅ Good: Japanese
feat(dialogue): 3段階ヒントシステムの実装

PRDに記載された3段階ヒントシステムを実装:
- レベル1: 問題理解の確認
- レベル2: 既習事項の想起
- レベル3: 部分的支援

Closes #42

# ❌ Bad: Too vague
update code

# ❌ Bad: No type
added new feature
```

---

## Commit Granularity

### Principles

- One logical change per commit
- Commits should be atomic
- Each commit should pass tests

### Examples

```bash
# ✅ Good: Appropriate granularity
git commit -m "feat(audio): add audio recording component"
git commit -m "feat(audio): integrate Web Audio API for level monitoring"
git commit -m "test(audio): add tests for audio recorder hook"

# ❌ Bad: Too large
git commit -m "feat: implement entire dialogue system with audio and hints"

# ❌ Bad: Too small (batch these)
git commit -m "fix: typo"
git commit -m "fix: another typo"
git commit -m "fix: one more typo"
```

---

## Pull Request

### PR Title

```
<type>(<scope>): <description>
```

**Examples:**

```
feat(dialogue): ソクラテス式対話エンジンの実装
fix(audio): WebSocket接続の切断問題を修正
refactor(components): コンポーネント構造の整理
docs(api): API仕様書の更新
```

### PR Template

```markdown
## 概要
<!-- この変更の概要を記載 -->

## 変更内容
<!-- 具体的な変更内容を箇条書きで -->
-
-
-

## 関連Issue
<!-- 関連するIssueをリンク -->
Closes #123

## テスト
<!-- テスト方法を記載 -->
- [ ] ユニットテスト追加
- [ ] 統合テスト追加
- [ ] 手動テスト完了

## スクリーンショット（該当する場合）
<!-- UI変更の場合はスクリーンショットを添付 -->

## チェックリスト
- [ ] コードレビュー依頼前に自己レビュー完了
- [ ] テストが全て通過
- [ ] ドキュメント更新（必要な場合）
- [ ] CLAUDE.mdの指針に従っている
```

---

## Code Review

### Reviewer Responsibilities

- Verify code correctness
- Check for security vulnerabilities
- Assess performance impact
- Confirm readability and maintainability
- Validate tests

### Review Checklist

```markdown
## Required Checks
- [ ] Meets functional requirements
- [ ] Sufficient tests (80%+ coverage)
- [ ] No security risks
- [ ] No performance degradation
- [ ] Follows coding conventions
- [ ] Documentation updated

## Recommended Checks
- [ ] Better implementation approach?
- [ ] Edge cases considered?
- [ ] Proper error handling?
- [ ] Appropriate logging?
```

---

## Review Process

### 1. Create PR

```bash
# 1. Create branch
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name

# 2. Implement changes
# - Small, reviewable units
# - 1 PR = 1 feature/fix

# 3. Self-review
# - Review your own code
# - Remove unnecessary comments/debug code
# - Run tests

# 4. Push and create PR
git push origin feature/your-feature-name
# Create PR on GitHub
```

### 2. Review Flow

```
Author: Create PR
  ↓
Reviewer 1: Initial review (within 1 business day)
  ↓
Author: Address feedback
  ↓
Reviewer 2: Second review (if needed)
  ↓
Approved → Merge
```

### 3. Merge Criteria

- Minimum 1 approval
- All CI checks passing
- No conflicts
- All comments resolved

---

## Best Practices

### 1. Small PRs

```bash
# ✅ Good: Focused PR
feat(audio): add audio recording component
- Added AudioRecorder component
- Integrated Web Audio API
- Added unit tests

# ❌ Bad: Too large
feat: implement entire dialogue system
- Added dialogue engine
- Added audio recording
- Added hint system
- Added evaluation system
- Added UI components
```

### 2. Descriptive Commits

```bash
# ✅ Good
feat(auth): implement JWT authentication with refresh tokens

Added JWT-based authentication:
- Access tokens (15min expiry)
- Refresh tokens (7day expiry)
- Token rotation on refresh

# ❌ Bad
update auth
```

### 3. Self-Review

Before creating PR:

- Review your own diff
- Check for debug code, console.logs
- Run linter and tests
- Verify documentation updates

### 4. Interactive Rebase

```bash
# Clean up commits before PR
git rebase -i develop

# Squash fixup commits
git commit --fixup <commit-hash>
git rebase -i --autosquash develop
```

---

## Common Workflows

### Feature Development

```bash
# 1. Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. Work on feature
git add .
git commit -m "feat(scope): description"

# 3. Keep up to date with develop
git fetch origin
git rebase origin/develop

# 4. Push and create PR
git push origin feature/new-feature
```

### Bug Fix

```bash
# 1. Create fix branch
git checkout develop
git pull origin develop
git checkout -b fix/bug-description

# 2. Fix bug
git add .
git commit -m "fix(scope): description"

# 3. Push and create PR
git push origin fix/bug-description
```

### Hotfix (Production)

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-issue

# 2. Fix issue
git add .
git commit -m "fix(scope): critical issue description"

# 3. Merge to main AND develop
git checkout main
git merge hotfix/critical-issue
git push origin main

git checkout develop
git merge hotfix/critical-issue
git push origin develop
```

---

## Git Configuration

```bash
# Recommended settings
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main
git config --global pull.rebase true
git config --global rebase.autoStash true
git config --global fetch.prune true
git config --global color.ui auto
```

---

## Troubleshooting

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Fix commit message
git commit --amend -m "new message"

# Stash changes
git stash
git stash pop

# Resolve conflicts
git fetch origin
git rebase origin/develop
# Edit conflicted files, then:
git add <file>
git rebase --continue
```

---

## Checklist

### Before Commit
- [ ] Code reviewed by yourself
- [ ] Tests pass locally
- [ ] Linter passes
- [ ] No debug code/console.logs
- [ ] Meaningful commit message

### Before PR
- [ ] Branch up to date with develop
- [ ] All tests pass
- [ ] PR description filled
- [ ] Related issues linked
- [ ] Self-review completed

### Before Merge
- [ ] Approved by reviewer(s)
- [ ] CI/CD checks pass
- [ ] Conflicts resolved
- [ ] Comments addressed

---

## References

- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

---

**Version 1.0** | **Use with**: `/frontend` `/tdd` for complete workflow
