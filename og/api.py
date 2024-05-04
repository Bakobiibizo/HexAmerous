import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}

if __name__ =="__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)