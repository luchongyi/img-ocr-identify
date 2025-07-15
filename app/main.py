from fastapi import FastAPI
from app.api import ocr, whitelist, user
from app.startup import startup_event, shutdown_event
from contextlib import asynccontextmanager
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

@asynccontextmanager
async def lifespan(app):
    await startup_event()
    yield
    await shutdown_event()

app = FastAPI(lifespan=lifespan)

app.include_router(ocr.router)
app.include_router(whitelist.router)
app.include_router(user.router)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)