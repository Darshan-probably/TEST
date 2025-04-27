from fastapi import FastAPI
import uvicorn



if __name__ == "__main__":
    app = FastAPI()
    uvicorn.run(app, port=8000, host="0.0.0.0")
