# ADR-0009: Starlette の multipart 警告（`python_multipart` 移行）対応方針

- **Status**: Draft  
- **Date**: 2025-11-03  
- **Deciders**: RT（アーキテクト / 実装担当）  
- **Supersedes**: なし  
- **Superseded by**: なし  

---

## Context
- Gateway サービスのテスト実行時、以下の警告が発生している：  
  ```
  PendingDeprecationWarning: Please use `import python_multipart` instead.
  ```
- これは **Starlette（FastAPIの依存）** 内部の `formparsers.py` が `import multipart` を使用していることに起因する。  
- Starlette チームは今後、`python_multipart` パッケージを明示的に使用する方向へ移行予定。  
- この警告自体は機能上の不具合ではないが、将来的な Breaking Change を示唆している。  
- CI 出力に警告が混在することでノイズとなり、テストの可読性や信頼性が低下する。

対象スコープ：
- `gateway` サービス（FastAPIベース）  
- 開発・CI/CD 環境（pytest 実行時）

---

## Decision
- 現段階では **警告を無視（suppress）しつつ、Starlette側の正式リリースに備える**。  
- `python-multipart` を明示的にインストールして依存関係を固定化し、将来の破壊的変更に備える。  
- 将来的に Starlette / FastAPI の更新で import 先が統一された段階で、本 ADR を Supersede する。

---

## Consequences

**Positive**
- CI 出力の安定化とノイズ低減。  
- 依存関係の固定化によりビルドの再現性を確保。  
- 今後の Starlette バージョンアップに柔軟に対応可能。

**Negative / Trade-offs**
- 警告自体は抑制のみで根本解決ではない。  
- 一部の Starlette バージョンで `python_multipart` の挙動が異なる可能性あり。  
- 依存更新時に再発する可能性がある。

---

## Alternatives Considered

- **代替案A: FastAPI / Starlette を最新バージョンに上げる**  
  - メリット：修正済みの可能性あり。  
  - 却下理由：依存連鎖により `strawberry-graphql` や `pydantic` の互換性が崩壊するリスクが高い。

- **代替案B: pytest 警告を完全無視（pytest -p no:warnings）**  
  - メリット：ログ出力がクリーン。  
  - 却下理由：他の有用な警告も抑制してしまうため非推奨。

---

## Implementation notes
- `requirements.txt` に明示的に追記：
  ```text
  python-multipart>=0.0.9
  ```

- pytest 設定（`pytest.ini`）に以下を追加：
  ```ini
  [pytest]
  asyncio_mode = auto
  filterwarnings =
      ignore::PendingDeprecationWarning
  ```

- Starlette のリリースノートを定期的に確認し、警告が解消された時点で除去予定。  
- CI 環境でも警告抑制設定を反映させ、ログノイズを防止。

---

## Links
- [Starlette GitHub: multipart parser migration issue](https://github.com/encode/starlette/issues)  
- ADR-0008: Pydantic v1固定の方針  
- ADR-0007: GraphQL Gateway を採用する  

---
