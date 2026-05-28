from fastapi import FastAPI

app = FastAPI()


@app.on_event("startup")
async def startup():
    await init_db()
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
