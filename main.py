from fastapi import FastAPI

app = FastAPI(title="HABITA Backend", version="1.0.0")


@app.get("/")
def root():
    return {"message": "HABITA backend running"}