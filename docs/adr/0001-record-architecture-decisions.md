# ADR-0001: record-architecture-decisions

- **Status**: Draft
- **Date**: 2025-11-02
- **Deciders**: Project Owner: RT
- **Supersedes**: -
- **Superseded by**: -

## Context
本プロジェクトでは、設計上の重要な意思決定が増えていく。
問題は、口頭やPRコメントに散らばると再利用性が落ち、過去判断の背景が追えなくなること。
設計レビュー、チーム合意、将来の振り返り、ポートフォリオ化を支える「単一の参照点」が必要。

## Decision
- すべての重要な設計判断は **ADR (Architecture Decision Record)** として `docs/adr/` 配下にMarkdownで保存する。
- 1つの意思決定につき1ファイル。命名は `NNNN-kebab-title.md`。
- 作成は `make adr ADR_NAME="kebab-title"` で行い、PRに含めてレビュー対象とする。
- 判断の変更は「差し替え」ではなく **新しいADRでSupersede** する。

## Consequences
**Positive**
- 判断の背景と代替案が残り、過去判断を再評価しやすい
- PR単位でレビュー可能（docs as code）
- 新メンバーのオンボーディングが速い

**Negative / Trade-offs**
- ドキュメント更新コストが増える
- 軽微な判断と重要判断の仕分けが必要

## Alternatives Considered
- Wiki/Notionに記録: 参照は容易だが、コード変更と乖離しやすい
- 口頭/PRコメント運用: 検索性・再現性が低い

## Implementation notes (optional)
- `ops/scripts/new_adr.sh` で自動採番
- `ADR_DUPLICATE_STRATEGY=version` で同一slugの派生を `-v2` で生成可能

## Links
- https://adr.github.io/