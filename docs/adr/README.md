# Architecture Decision Records (ADRs)

- 形式: 1 ADR = 1 Markdown
- 命名: `NNNN-kebab-title.md`（0010 以降もゼロ埋め継続）
- ステータス: `Accepted | Draft | Superseded`
- 原則: 1つの意思決定に1つのADR。迷ったら分割。

## ワークフロー
1. 新規作成: `make adr NAME="my-decision-title"`
2. 内容を編集して PR に含める（コードと一緒にレビュー）
3. 変更があれば新しいADRで **Supersede** する

## 参考
- https://adr.github.io/