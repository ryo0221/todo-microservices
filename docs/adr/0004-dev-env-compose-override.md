# ADR-0004: Local Dev with Docker Compose Override & Hot Reload

- **Status**: Draft
- **Date**: 2025-11-02
- **Deciders**: Project Owner: RT
- **Supersedes**: —
- **Superseded by**: —

## Context
コード変更のたびに再ビルドすると反復速度が落ちる。学習と反復を高速化し、TDDを回しやすくするため、依存更新以外はビルドを避けたい。

## Decision
- `docker-compose.override.yml` を導入し、ローカル開発では
  - `app/` と `tests/` を **bind mount**
  - Uvicorn `--reload` で **ホットリロード**
- 依存（`requirements.txt`）更新時のみ対象サービスを再ビルド

## Consequences
**Positive**
- 反復が速く、テスト駆動がやりやすい
- サービス間疎通を常時確認できる

**Negative / Trade-offs**
- 本番との差異（reload/監視）があるためCIでの再現性に注意
- WSL/ネットワークドライブでは監視の安定化が必要な場合あり

## Alternatives Considered
- 変更のたびにビルド：単純だが開発速度が低下
- ローカルPython直実行：依存や疎通の管理が大変

## Implementation notes (optional)
- `WATCHFILES_FORCE_POLLING=1` を利用（監視の安定化）
- 必要に応じて `--reload-delay` を調整
- テストは `docker compose run ... pytest` でホットに回す

## Links
- Docker Compose docs