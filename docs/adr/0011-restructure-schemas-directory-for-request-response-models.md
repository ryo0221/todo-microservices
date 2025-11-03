# ADR-0011: `schemas/` ディレクトリにリクエスト／レスポンスモデルを整理する

- **Status**: Draft  
- **Date**: 2025-11-03  
- **Deciders**: RT  
- **Supersedes**: なし  
- **Superseded by**: なし  

---

## Context

- 現在、FastAPIエンドポイントの各ルート (`routes_auth.py`, `routes_todos.py` など) では、
  `RegisterRequest`, `LoginRequest`, `TokenResponse` などのスキーマが直接定義・使用されている。  
- 規模の拡大により、認証、Todo、Gateway など各サービスごとにデータモデルが増加しており、
  ルート層でのスキーマ管理は保守性・一貫性を損ねている。  
- Pydantic モデルの用途が「DBモデリング」 (`models/`) と「I/Oスキーマ」 (`schemas/`) に混在している現状があり、  
  DDD的な責務分離の観点からも整理が求められる。

---

## Decision

- 各サービス（例：`auth`, `todo`）配下に `schemas/` ディレクトリを設け、  
  **入出力スキーマ（Pydanticモデル）をルート層から分離**する。  
- `schemas/` 内では以下の命名・分類ルールを採用する。  

```
app/
 ├── api/
 │   ├── routes_auth.py
 │   └── routes_todos.py
 ├── core/
 ├── db/
 ├── models/
 ├── schemas/
 │   ├── auth.py        # RegisterRequest, LoginRequest, TokenResponse, RefreshRequest など
 │   ├── todo.py        # TodoCreate, TodoResponse, TodoUpdate など
 │   └── common.py      # 共通レスポンスやエラーモデル
 └── main.py
```

---

## Consequences

**Positive**

- 各ルート層からビジネスロジックとデータ定義が分離され、見通しが良くなる  
- API入出力モデルの共通化・再利用が容易になる（例：GraphQL Gateway側でもimport可能）  
- スキーマの型安全性を強化し、OpenAPIドキュメント出力も自動的に整理される  

**Negative / Trade-offs**

- スキーマ修正時に import 経路が長くなる (`from app.schemas.auth import RegisterRequest`)  
- 各サービスごとに `schemas/` ディレクトリを維持する運用コストが発生  
- ディレクトリ階層が1段深くなり、小規模時点ではやや冗長に見える可能性  

---

## Alternatives Considered

- **代替案A: ルートファイル直下で定義する（現状維持）**  
  → スモールスケールではシンプルだが、拡張性に欠ける。  
- **代替案B: モデルをDB層にまとめる**  
  → ORMモデルとI/Oモデルの責務が混在し、保守性が低下する。  

---

## Implementation notes

- `schemas/auth.py` に以下のように統一する：

```python
from pydantic import BaseModel

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str

class RefreshRequest(BaseModel):
    refresh_token: str
```

- 各ルート (`routes_auth.py` など) では：

```python
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
```

---

## Links

- PR: _[to be added]_  
- Related ADR: [ADR-0002: Service Split (auth / todo)](./0002-service-splite-auth-todo.md)  