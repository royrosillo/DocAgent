from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.webhook import router as webhook_router
from app.api.docs import router as docs_router

app = FastAPI(
    title="DocAgent API",
    description="AI-powered code documentation agent",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restringir en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(docs_router, prefix="/docs-api", tags=["documentation"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
