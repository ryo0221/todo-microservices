# ADR-0006: Place API Gateway at the Repository Root (parallel to `services/`)

- **Status**: Draft
- **Date**: 2025-11-02
- **Deciders**: Project Owner RT
- **Supersedes**: -
- **Superseded by**: -

## Context
API Gateway は個々のアプリケーションサービス（Auth / Todo）の“内側”ではなく、**クライアントと各サービスの境界に立つコンポーネント**である。  
将来的に CORS、観測性（構造化ログ、トレーシング、リクエストID）、レート制限、A/Bテスト、GraphQL Gateway、BFF（Backend for Frontend）など**横断関心事を集約**する役割を担う可能性が高い。

以前の候補として、`services/gateway` として「1マイクロサービス」と同列に置く案も検討したが、 **境界上の“フロントドア”** としての性質を明確にする構成が望ましい。

## Decision
- リポジトリ直下に **`gateway/` ディレクトリ**を置き、`services/`（アプリケーションサービス群）と**並列**に配置する。  
  - `gateway/` … ルーティング、認可前段の検証、CORS、レート制限、観測性の集約地点  
  - `services/` … Auth / Todo など、ビジネスロジックの所有者
- Compose では `gateway` を**外向けエントリポイント**（例: `http://localhost:8080`）に設定し、`/auth/*`、`/todos/*` を各サービスへプロキシする。

## Consequences
### Positive
- **横断関心の集約**：CORS、ログ、レート制限、トレース、リクエストIDを一箇所で適用可能  
- **将来拡張に適合**：GraphQL Gateway / BFF への**発展余地**を確保  
- **境界の明確化**：`services/` の実装と、外部公開ポリシーの責務分離  
- **運用容易性**：ゲートウェイ単体でカナリア/シャドーイング/ABテスト等の**トラフィック戦略**を実装しやすい

### Negative / Trade-offs
- **初期の複雑性増**：モノリスや単純なAPI直公開よりセットアップが多い  
- **二重の設定ポイント**：サービス側とゲートウェイ側で CORS/認可設定が重複しやすい（ガイドライン整備で緩和）

## Alternatives Considered
- **A. `services/gateway`（サービスの一員として配置）**  
  - *Pros*: 単純、サービスと同じ運用フロー  
  - *Cons*: 境界としての役割が曖昧になり、BFF/GraphQL への発展で**階層変更が必要**になりがち
- **B. モノリス直公開（ゲートウェイ無し）**  
  - *Pros*: 最短で動く  
  - *Cons*: 横断関心が各サービスに分散し**重複/不整合**が発生、将来の集約が困難
- **C. サービスメッシュのみ（L7ゲートウェイを置かない）**  
  - *Pros*: Pod間通信やmTLSなど“東西トラフィック”の統制に強い  
  - *Cons*: **北南トラフィック**のポリシー（CORSや公開ルーティング）を集約できない

## Implementation Notes (Optional)
- 最初は FastAPI + httpx での**薄いリバースプロキシ**で開始し、段階的に  
  - CORS（ホワイトリスト、プリフライト短絡）  
  - 構造化ログ（`request_id`、`user_id`、`route`）  
  - レート制限（IP / user / route 単位）  
  - ルーティング表の設定ファイル化（YAML/ENV）  
  を導入する。
- ディレクトリ例

```
.
├── gateway/                       # API Gateway / BFF entrypoint
│   ├── app/
│   │   ├── main.py               # FastAPI entrypoint
│   │   ├── proxy.py              # Reverse proxy logic
│   │   ├── middleware/
│   │   │   ├── cors.py           # CORS & preflight
│   │   │   ├── logging.py        # Request ID & access log
│   │   │   └── rate_limit.py     # Basic rate limiting (future)
│   │   ├── settings.py           # Env & config
│   │   └── routes/               # Route forward rules (optional)
│   ├── tests/                    # Gateway integration tests
│   └── Dockerfile
│
├── services/
│   ├── auth/                     # Auth service (JWT issuance)
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── models/
│   │   │   ├── routes/
│   │   │   ├── core/
│   │   │   ├── db/
│   │   │   └── security/         # Password hashing, JWT utils
│   │   ├── tests/
│   │   └── Dockerfile
│   │
│   └── todo/                     # Todo service (domain logic)
│       ├── app/
│       │   ├── main.py
│       │   ├── models/
│       │   ├── routes/
│       │   ├── core/
│       │   └── db/
│       ├── tests/
│       └── Dockerfile
│
├── infra/                        # Runtime & dev environment
│   └── docker/
│       ├── docker-compose.yml
│       ├── docker-compose.override.yml
│       └── env/
│           ├── auth.env
│           └── todo.env
│
├── docs/
│   └── adr/                      # Architecture Decision Records
│       ├── 0001-*.md
│       └── _template.md
│
└── ops/                          # Automation, CI hooks, scripts
    ├── scripts/
    └── Makefile
```

## Links
- ADR: Split Services into Auth and Todo (with API Gateway)
- ADR: Local Dev with Docker Compose Override & Hot Reload
- ADR: Adopt TDD for Microservices