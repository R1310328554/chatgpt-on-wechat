import os

if __name__ == "__main__":
    # import needed here when running main.py to debug backend
    # you will need to run pip install python-dotenv
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
import sentry_sdk
from fastapi import FastAPI, HTTPException, logger
from fastapi.responses import JSONResponse 
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
# from middlewares.cors import add_cors_middleware
from bot.LangchainChatchat.bot_routes import brain_router


if os.getenv("DEV_MODE") == "true":
    import debugpy

    logger.debug("👨‍💻 Running in dev mode")
    debugpy.listen(("0.0.0.0", 5678))


# sentry_dsn = os.getenv("SENTRY_DSN")
# if sentry_dsn:
#     sentry_sdk.init(
#         dsn=sentry_dsn,
#         sample_rate=0.1,
#         enable_tracing=True,
#         integrations=[
#             StarletteIntegration(transaction_style="endpoint"),
#             FastApiIntegration(transaction_style="endpoint"),
#         ],
#     )

app = FastAPI()

# add_cors_middleware(app)

app.include_router(brain_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# handle_request_validation_error(app)

def startHttpServer():
# if __name__ == "__main__":
    # run main.py to debug backend
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5050)
