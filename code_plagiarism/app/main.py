from fastapi import FastAPI
from app.routes.plagiarism_routes import router as plagiarism_router


app = FastAPI(
    title="EduSaaS Code Plagiarism Service",
    version="1.0.0"
)


app.include_router(plagiarism_router)


@app.get("/")
def root():
    return {
        "service": "EduSaaS Code Plagiarism Detection",
        "status": "running"
    }