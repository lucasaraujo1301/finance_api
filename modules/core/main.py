from fastapi import FastAPI

from modules.core.middlewares import ProcessTimeMiddleware

app = FastAPI()
app.add_middleware(ProcessTimeMiddleware)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
