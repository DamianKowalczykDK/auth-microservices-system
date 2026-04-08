from fastapi import FastAPI, APIRouter
from apigateway.api.routes import auth, admin, account, user
import logging


logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="API Gateway",
    description="API Gateway",
    version="1.0.0"
)


@app.get("/", response_model=dict[str, str], tags=["Root"])
async def healthcheck() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "apigateway"
    }

router = APIRouter(prefix="/api")
router.include_router(auth.router)
router.include_router(admin.router)
router.include_router(account.router)
router.include_router(user.router)

app.include_router(router)

