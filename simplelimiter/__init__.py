import logging
import redis

from typing import Optional
from fastapi import Request, HTTPException, Response

TIME_EQUIVALENT_IN_SECONDS = {
    "second": 1,
    "minute": 60,
    "hour": 3600,
    "day": 86400
}


class Limiter:
    redis: redis = None
    ignore_limiter: bool
    debug: bool
    requests: int
    timeunit: str
    exp_time: int

    def __init__(self, requests_slash_timeunit):
        requests, timeunits = requests_slash_timeunit.split("/")
        self.requests = int(requests)
        self.timeunit = timeunits
        self.exp_time = TIME_EQUIVALENT_IN_SECONDS[timeunits]

    async def __call__(self, request: Request, response: Response):
        if self.ignore_limiter:
            return

        if not self.redis:
            logging.warning("No redis instance was provided")
            return

        identifier = self.get_identifier(request)
        requested_by_client = int(self.redis.get(identifier) or 0)

        if requested_by_client >= self.requests:
            raise HTTPException(status_code=429)

        requested_by_client = self.redis.incr(identifier)

        if requested_by_client == 1:
            self.redis.expire(identifier, self.exp_time)
            ttl = self.exp_time
        else:
            ttl = self.redis.ttl(identifier)

        if self.debug:
            logging.info(f"Limiter [{identifier}] will expire in {ttl}")

    @classmethod
    def init(
        cls, 
        redis_instance: redis, 
        debug: Optional[bool] = False,
        ignore_limiter: Optional[bool] = False
    ):
        cls.debug = debug
        cls.redis = redis_instance
        cls.ignore_limiter = ignore_limiter

    @staticmethod
    def get_identifier(request: Request) -> str:
        request_ip = request.client.host
        identifier = f"LIMITER:{request_ip}:{request.url.path}"

        return identifier
