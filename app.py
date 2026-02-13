import uvicorn
from backend.main import app
from backend.config import settings

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
