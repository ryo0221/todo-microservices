# ADR-0010: Gateway における統一ミドルウェア構成方針（CORS / Logging / RateLimit）

- **Status**: Draft  
- **Date**: 2025-11-03  
- **Deciders**: RT（アーキテクト / 実装担当）  
- **Supersedes**: なし  
- **Superseded by**: なし  

---

## Context
- Gateway サービスは複数のマイクロサービス（`auth`, `todo` など）へのエントリポイントとなる。  
- 各サービス間で共通する「横断的関心事（Cross-cutting Concerns）」が存在する：  
  - **CORS（クロスオリジンアクセス）制御**
  - **アクセスログ（構造化ログ出力）**
  - **レート制限（DoS / 乱用防止）**
- これらを各マイクロサービスごとに実装すると、重複・不整合・運用負荷が増加する。  
- よって Gateway に集約し、**リバースプロキシ + BFF（Backend for Frontend）層** として統一管理することを決定。

対象スコープ：
- `gateway` サービス（FastAPIベース）  
- 上位クライアント（Web / モバイルアプリ）および CI/CD 環境

---

## Decision
- 3つの横断関心をすべて Gateway に統一実装する。  
- 各ミドルウェアを独立モジュールとして実装し、`app/middleware/` 以下に配置：  
  ```
  gateway/app/middleware/
  ├── cors_preflight.py
  ├── logging_middleware.py
  └── rate_limit_middleware.py
  ```
- 実装順序（スタック順）は以下の通り：
  1. **CORSPreflightMiddleware** — ブラウザ起点の OPTIONS リクエスト処理  
  2. **RateLimitMiddleware** — 高頻度アクセス制御（429応答）  
  3. **LoggingMiddleware** — すべての通信を構造化JSONログとして記録  

---

## Consequences

**Positive**
- CORS, Logging, RateLimit が統一ポリシーで適用され、保守性・可観測性が向上。  
- ミドルウェア単位で責務分離でき、テスト容易性が高い（pytestによる単体検証済み）。  
- Gateway に集約することで、各マイクロサービスは純粋に業務ロジックへ集中可能。

**Negative / Trade-offs**
- Gateway が単一障害点（SPOF）になりやすい。  
- レート制限の閾値・状態を複数インスタンス間で共有する必要がある（Redis等による分散カウンタ管理が将来的課題）。  
- CORS と BFF の両立により設定が複雑化する恐れあり。

---

## Alternatives Considered

- **代替案A: 各マイクロサービスが独自にCORS/ログ制御を持つ**
  - メリット：サービス単体の独立性を維持。
  - 却下理由：実装重複とポリシー分散を招く。

- **代替案B: API Gateway（NGINX / Envoy）を外部導入**
  - メリット：高スループット・集中管理。
  - 却下理由：学習コスト・構成管理コストが高く、開発初期段階では過剰。

---

## Implementation notes

- **CORSPreflightMiddleware**
  ```python
  from starlette.middleware.base import BaseHTTPMiddleware
  from starlette.responses import Response

  class CORSPreflightMiddleware(BaseHTTPMiddleware):
      async def dispatch(self, request, call_next):
          if request.method == "OPTIONS":
              return Response(status_code=204, headers={
                  "Access-Control-Allow-Origin": "*",
                  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                  "Access-Control-Allow-Headers": "*",
              })
          response = await call_next(request)
          response.headers["Access-Control-Allow-Origin"] = "*"
          return response
  ```

- **LoggingMiddleware**
  - 構造化 JSON 形式でログ出力：
    ```json
    {"method": "GET", "path": "/todos", "status_code": 200, "duration_ms": 12.3}
    ```

- **RateLimitMiddleware**
  - シンプルな in-memory カウンタを使用。  
  - 将来的には Redis による分散レート制御へ移行予定。  

- **適用順序**
  ```python
  app.add_middleware(CORSPreflightMiddleware)
  app.add_middleware(RateLimitMiddleware)
  app.add_middleware(LoggingMiddleware)
  ```

---

## Links
- ADR-0006: Gateway ディレクトリ構成の採用理由  
- ADR-0007: GraphQL Gateway の導入方針  
- ADR-0009: Starlette multipart 警告対応方針  

---
