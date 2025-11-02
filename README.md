# TODO app

## 鳥観図

```
[ Client ] ──▶ [ API Gateway ] ──▶  /auth/*  ─▶ [ Auth Service ] ──▶ [ Postgres (auth) ]
                        │
                        └─────────▶  /todos/* ─▶ [ Todo Service ] ──▶ [ Postgres (todo) ]
(任意) 監視/分散トレース: [ Prometheus / Grafana / Jaeger / OpenTelemetry Collector ]
(任意) 非同期イベント:   [ RabbitMQ or Redis ]  ← 第2フェーズで導入
```

* API Gateway\
クライアントとの唯一の接点。ルーティングと共通の責務（リクエストログ、レート制限、CORS、認証ヘッダの検証）を集約し、サービスを疎結合に保ちます。

* Auth Service\
ユーザ登録/ログイン、JWT発行、鍵のローテーションなど **認証の境界（bounded context）** を明確化。

* Todo Service\
TodoのCRUDに集中。AuthからのJWTを検証しつつ、自分のDBだけを直接更新（“各サービスが自分のデータのオーナー”を徹底）。

* DBはサービスごとに分割\
「スキーマ共有＝暗黙的な結合」を避けるのがMSAの基本。ローカルではコストを下げるため同一Postgresコンテナ内に別DBでもOK（後述）。

* 観測性（Observability\
マイクロサービスは追跡が難しくなるので、構築初期からログ/メトリクス/トレースの経路を用意すると後悔が少ないです。

```
todo-microservices/
├─ services/
│  ├─ auth/
│  │  ├─ app/                      # "src-layout": ランタイムのPythonコード
│  │  │  ├─ main.py                # FastAPI起動点（routerマウント）
│  │  │  ├─ api/                   # ルータ（/auth/login, /auth/register など）
│  │  │  ├─ core/                  # 設定・セキュリティ・依存性（JWT, settings, deps）
│  │  │  ├─ models/                # ORMモデル（SQLModel/SQLAlchemy）
│  │  │  ├─ schemas/               # Pydanticスキーマ（I/O境界の契約）
│  │  │  └─ db/                    # セッション管理、初期化
│  │  ├─ tests/                    # ユニット/統合テスト
│  │  ├─ alembic/                  # マイグレーション（DB進化の安全弁）
│  │  ├─ pyproject.toml            # 依存関係 & ビルド設定
│  │  ├─ Dockerfile
│  │  └─ .env.example              # 環境変数の雛形（秘密は入れない）
│  │
│  └─ todo/
│     ├─ app/
│     │  ├─ main.py
│     │  ├─ api/                   # /todos/* CRUD
│     │  ├─ core/                  # 認可（JWT検証）、設定、共通依存
│     │  ├─ models/
│     │  ├─ schemas/
│     │  └─ db/
│     ├─ tests/
│     ├─ alembic/
│     ├─ pyproject.toml
│     ├─ Dockerfile
│     └─ .env.example
│
├─ gateway/
│  ├─ app/
│  │  ├─ main.py                    # ルーティング/プロキシ/共通ミドルウェア
│  │  └─ settings.py
│  ├─ tests/
│  ├─ pyproject.toml
│  └─ Dockerfile
│
├─ infra/
│  ├─ docker/
│  │  ├─ docker-compose.yml         # ローカル起動の単一源
│  │  └─ traefik/                   # 例: Traefik/Nginx設定（TLSは後で）
│  └─ k8s/                          # 第3フェーズ以降（Minikube/EKSなど）
│
├─ ops/
│  ├─ Makefile                      # `make up`, `make test`, `make migrate` など
│  └─ scripts/                      # 補助スクリプト（DB初期化等）
│
├─ docs/
│  ├─ architecture.md               # コンテキスト/決定の記録（ADR）
│  └─ openapi/                      # サービスごとのOpenAPI（契約の可視化）
│
├─ .env.example                     # ルート共通の通知/ポートなど
└─ README.md                        # 起動手順、開発規約
```

**なぜこの分け方？**

* services/<name>/app/{api,core,models,schemas,db}\
FastAPIでは「API（境界）」「スキーマ（契約）」「ドメインモデル（DB）」「設定/認証（core）」を分けると、
  * 変更の影響範囲が明確
  * テストが書きやすい
  * 将来の言語/フレームワーク変更にも耐えやすい

* サービスごとの独立Dockerfile/pyproject\
依存を局所化し、それぞれが独立ビルド/独立デプロイできるように。

* alembic/
DBは“生き物”。スキーマ進化を履歴管理できないとMSAは破綻しやすいです。

* gateway/ は別プロセス
リバースプロキシを別にすることで横断関心（CORS, ログ, レート制限）をひと所で扱える。のちにGraphQLゲートウェイや**BFF（Backend for Frontend）**にも進化可能。

* infra/ と ops/ を分離
“プロダクトのコード”と“デプロイ/運用のコード”を分けると、ローカル開発→本番の移行が楽。
infra/docker/docker-compose.yml を単一の真実源（SSOT）にして、開発者は make up で全スタックを上げられるようにします。

* docs/
仕様はコードと同じリポ内に。OpenAPIを吐き出して置いておくと、ツールレスでも“契約”をすぐ確認できます。