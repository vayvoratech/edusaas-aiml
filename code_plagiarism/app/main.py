from fastapi import FastAPI
from app.routes.plagiarism_routes import router as plagiarism_router
from app.routes.mini_project_plagiarism import router as mini_project_router

app = FastAPI(
    title="EduSaaS Code Plagiarism Service",
    version="1.0.0"
)


app.include_router(plagiarism_router)
app.include_router(mini_project_router)

@app.get("/")
def root():
    return {
        "service": "EduSaaS Code Plagiarism Detection",
        "status": "running"
    }