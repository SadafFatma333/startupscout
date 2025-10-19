# Minimal FastAPI app for Railway deployment
import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="StartupScout API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Metrics
START_TIME = time.time()
REQUEST_COUNT = 0

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "StartupScout API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    
    return {
        "status": "healthy",
        "uptime_sec": round(time.time() - START_TIME, 1),
        "requests": REQUEST_COUNT,
        "timestamp": time.time()
    }

@app.get("/stats")
async def get_stats():
    """Basic stats endpoint."""
    global REQUEST_COUNT
    
    return {
        "requests": REQUEST_COUNT,
        "uptime_sec": round(time.time() - START_TIME, 1),
        "status": "running"
    }

@app.get("/ask")
async def ask_endpoint(question: str = None):
    """Minimal ask endpoint."""
    if not question:
        return {"error": "Question parameter is required"}
    
    return {
        "question": question,
        "answer": "This is a minimal version of StartupScout. Full RAG functionality requires additional dependencies.",
        "references": [],
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
