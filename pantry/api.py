# pantry/api.py
from fastapi import FastAPI

from pantry.barcode import barcode_to_json
from pantry.db import add_preserve, remove_preserve


def create_app() -> FastAPI:
    app = FastAPI(title="Pantry Manager")

    @app.get("/")
    async def root():
        return {"message": "Pantry Manager API running"}

    @app.post("/add/{barcode}")
    async def add_item(barcode: str):
        preserve = barcode_to_json(barcode)
        count = add_preserve(preserve)
        return {"status": "added", "count": count}

    @app.post("/remove/{barcode}")
    async def remove_item(barcode: str):
        preserve = barcode_to_json(barcode)
        count = remove_preserve(preserve)
        return {"status": "removed", "count": count}

    return app