from fastapi import FastAPI

from app.api.compare import router as compare_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Letrus Plagiarism Service",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(compare_router, prefix="")
    return app


app = create_app()
