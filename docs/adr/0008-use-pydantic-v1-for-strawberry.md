# ADR-0008: Strawberry互換性のために Pydantic v1 を固定する

- **Status**: Draft  
- **Date**: 2025-11-03  
- **Deciders**: RT（アーキテクト / 実装担当）  
- **Supersedes**: なし  
- **Superseded by**: なし  

---

## Context
- Gateway サービスで採用している **Strawberry GraphQL** は、現在（2025年11月時点）において **Pydantic v2 系との完全互換性がない**。  
- 特に `strawberry.experimental.pydantic` モジュール内で `pydantic._internal._typing_extra.is_new_type` を参照しており、これは v2 系で削除されている内部実装依存の関数である。  
- そのため、`ImportError: cannot import name 'is_new_type' from 'pydantic._internal._typing_extra'` というエラーが発生し、テスト実行およびアプリ起動が不能となった。  
- 当プロジェクトでは **GraphQL Gateway の早期実装と安定運用** を優先するため、Pydantic のメジャーバージョン固定を決定する。

対象スコープ：
- `gateway` サービス（`strawberry-graphql[fastapi]` を利用）  
- Poetry / requirements.txt での依存管理設定

---

## Decision
- Pydantic のバージョンを **v1 系に固定**する。  
  ```text
  pydantic>=1.10,<2.0
  ```
- Strawberry が Pydantic v2 を正式サポートするまで、この制約を維持する。  
- 今後 v2 対応が完了した段階で再評価を行う（Supersede予定）。

---

## Consequences

**Positive**
- Strawberry GraphQL による Gateway 機能を安定稼働させられる。  
- FastAPI / Strawberry / httpx 間の依存衝突を回避できる。  
- テスト（pytest）実行環境が安定化し、CI/CD が確立できる。

**Negative / Trade-offs**
- 新しい Pydantic v2 の機能（ValidationModel APIなど）が利用できない。  
- 将来的にバージョンアップ時の移行工数が発生する。  
- 他のサービス（auth / todo）で Pydantic v2 を採用した場合、Gateway との型整合性の差が生じるリスクがある。

---

## Alternatives Considered

- **代替案A: Pydantic v2 に合わせて Strawberry 側コードをパッチ修正**  
  - メリット：依存の統一。  
  - 却下理由：Strawberry の内部実装変更リスクが高く、公式対応前に独自修正するのは保守コストが高い。

- **代替案B: GraphQL Gateway 実装を一時的にスキップ**  
  - メリット：依存問題を回避。  
  - 却下理由：Gateway 開発ロードマップが停滞する。

---

## Implementation notes
- `requirements.txt` に以下を明記：  
  ```text
  strawberry-graphql[fastapi]==0.247.0
  pydantic>=1.10,<2.0
  ```
- 既存の Docker ビルドキャッシュをクリアして再ビルドが必要。  
  ```bash
  docker compose build --no-cache gateway
  ```
- Pydantic v2 対応が公式に完了した際は、再度依存関係を見直す。

---

## Links
- [Strawberry Issue #2581: Pydantic v2 support tracking](https://github.com/strawberry-graphql/strawberry/issues/2581)  
- ADR-0007: GraphQL Gateway を採用する  


---
