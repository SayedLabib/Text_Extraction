from fastapi import FastAPI
from app.api.routes import router as api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION
)

# Define main variable pointing to the app instance to fix ASGI loading issue
main = app

@app.get("/")
async def root():
    """
    Welcome endpoint with usage instructions
    """
    return {
        "message": "Welcome to the Text Extraction API",
        "usage": "POST a file to /extract-text/ endpoint to extract text",
        "supported_formats": settings.SUPPORTED_FORMATS
    }


# Include API routes
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)