# simplelimiter

A simple FastAPI rate limiter

## Requirements

[Redis](https://redis.io/)

## How to use


```py
import redis

from fastapi import FastAPI, APIRouter, Request
from fastapi.params import Depends
from simplelimiter import Limiter


app = FastAPI()
router = APIRouter()

# We initialize the Limiter on the app startup event
@app.on_event("startup")
async def startup():
    r = redis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    Limiter.init(redis_instance=r, debug=True)

    return app


# We pass the Limiter as a dependencie
@router.get("/", dependencies=[Depends(Limiter("5/minute"))])
def base_route(request: Request):
    return {"response": "ok"}


app.include_router(router)
```

