# ADR-NNNN: Adopt TDD for Microservices (Auth & Todo)

- **Status**: Draft
- **Date**: 2025-11-02
- **Deciders**: Project Owner, Core Devs
- **Supersedes**: —
- **Superseded by**: —

## Context
マイクロサービスでは変更点/結合点が多い。手動確認やE2Eのみだと回帰検出が難しい。学習効率と品質保証を両立するため、テスト駆動開発（TDD）を基盤とする。

## Decision
- **ユニット/機能テストを先に書く**（pytest + FastAPI TestClient）
- DBはテスト時 **SQLite + 依存差し替え** で高速化
- 仕様はテストで固定し、最小実装で緑 → リファクタの順で進める

## Consequences
**Positive**
- 回帰の自動検出、spec-as-testで設計が明確
- 依存の入替え（例：bcrypt→PBKDF2）も安全
- CI/CD へ展開しやすい

**Negative / Trade-offs**
- 初期のテスト記述コスト
- テスト設計スキルの学習が必要

## Alternatives Considered
- 事後テスト/手動中心：速度は出るが品質・再現性が不安定
- E2Eのみ：カバレッジが粗く、失敗時の切り分けが困難

## Implementation notes (optional)
- `conftest.py` で `get_db` をオーバーライド
- `sqlite:///:memory:` + `StaticPool` でメモリDBを共有
- テストは `services/<svc>/tests/` に配置、Docker上で実行

## Links
- ADR: SQLite StaticPool for Tests