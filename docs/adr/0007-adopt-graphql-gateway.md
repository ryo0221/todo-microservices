# ADR-0007: GraphQL Gateway を採用する

- **Status**: Draft  
- **Date**: 2025-11-03  
- **Deciders**: RT（アーキテクト / 実装担当）  
- **Supersedes**: なし  
- **Superseded by**: なし  

---

## Context
- 現在、`Auth` サービス（認証・JWT発行）と `Todo` サービス（タスク管理）の 2 つの REST API が稼働している。  
- フロントエンドから複数サービスを跨いでデータを取得する必要があり、API 呼び出しの重複や集約処理の煩雑化が課題となっている。  
- 各サービスのスキーマやエンドポイントが独立しており、クライアント側でのデータ統合コストが高い。  
- 今後サービスが増えることを想定し、より柔軟かつ拡張性のあるデータ取得方式が求められた。

対象スコープ：
- `gateway` サービス
- REST ベースの既存バックエンド（`auth`, `todo`）
- 将来的に追加される可能性のあるマイクロサービス群

---

## Decision
- **GraphQL Gateway** を新たに導入し、REST サービス群の前段に配置する。  
- 実装は **FastAPI + Strawberry GraphQL** により構築。  
- 単一エンドポイント `/graphql` で、Auth・Todo 両サービスのデータを統合的に取得できるようにする。  
- Gateway は BFF（Backend for Frontend）としても機能し、将来的な GraphQL Federation や gRPC 連携も視野に入れる。

---

## Consequences

**Positive**
- クライアントが必要なデータのみを宣言的に取得できる（過剰/過少フェッチ解消）。  
- 型安全なスキーマ定義により開発効率・保守性が向上。  
- Gateway 層に認証・ロギング・レート制限などの横断関心を集約できる。  
- フロントエンド側の API 統合ロジックを削減できる。

**Negative / Trade-offs**
- Gateway の導入により、ネットワークホップが 1 段階増加する。  
- GraphQL スキーマの設計・保守に専門的知識が必要となる。  
- REST サービスの変更と GraphQL スキーマ更新を同期させる運用コストが発生。  
- 初期構築・スキーマ連携の学習コストが増加。

---

## Alternatives Considered

- **代替案A: REST Gateway（現状維持）**  
  - メリット：構成が単純で実装コストが低い。  
  - 却下理由：クライアント側のデータ集約ロジックが複雑化する。拡張性が低い。

- **代替案B: gRPC Gateway**  
  - メリット：高パフォーマンスでスキーマ駆動。  
  - 却下理由：ブラウザクライアントとの親和性が低い（HTTP/2依存）。

- **代替案C: 部分的 GraphQL 導入（Hybrid）**  
  - メリット：リスクを分散できる。  
  - 却下理由：統合ポイントが不明確になり、保守負荷が高まる。

---

## Implementation notes
- `strawberry-graphql[fastapi]==0.247.0` を使用。  
- Gateway のディレクトリは `services/` と並列に配置（参照: ADR-0006）。  
- 各 REST サービスとは `httpx.AsyncClient` により非同期通信を行う。  
- GraphQL スキーマ定義は `gateway/app/graphql/schema.py` に集約。  
- 最初の実装は `query { hello }` による疎通確認テスト（TDDにより検証済み）。

---

## Links
- [Strawberry GraphQL Docs](https://strawberry.rocks/docs/integrations/fastapi)  
- [GraphQL Official Spec](https://spec.graphql.org/)  
- ADR-0006: Gateway Directory Placement  
- ADR-0010: Unified Middleware Architecture  
