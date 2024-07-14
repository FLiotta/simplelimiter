import os
import redis
from unittest import TestCase
from simplelimiter import Limiter
from starlette.testclient import TestClient

from fastapi import FastAPI, APIRouter, Request
from fastapi.params import Depends

def create_app():
    app = FastAPI()

    @app.on_event("startup")
    async def startup():
        redis_host = os.environ.get("REDIS_HOST")
        redis_port = os.environ.get("REDIS_PORT")
        redis_url = f"redis://{redis_host}:{redis_port}"
        redis_instance = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        Limiter.init(redis_instance=redis_instance, debug=True)

        return app

    router = APIRouter()

    @router.get("/", dependencies=[Depends(Limiter("5/second"))])
    def foo():
        return {"response": "ok"}

    app.include_router(router)

    return app


app = create_app()


class TestSimpleLimiter(TestCase):
    def test_simple(self):
        with TestClient(app) as client:
            response = client.get("/")
            assert response.status_code == 200

            response = client.get("/")
            assert response.status_code == 200

            response = client.get("/")
            assert response.status_code == 200

            response = client.get("/")
            assert response.status_code == 200

            response = client.get("/")
            assert response.status_code == 200

            response = client.get("/")
            assert response.status_code == 429
