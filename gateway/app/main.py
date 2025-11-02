from fastapi import FastAPI

app = FastAPI(title="API Gateway (stub)")

@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}

# ※ 本格的なリバースプロキシ/ルーティングは後続で実装します。