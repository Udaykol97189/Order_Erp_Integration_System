from fastapi import FastAPI

app = FastAPI(
    title="Integrated Sales & Order Management API",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}