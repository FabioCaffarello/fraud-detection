from fastapi import FastAPI

from adapters.controllers import emulator_controller

app = FastAPI(
    title="Emulator Service REST API",
    description="API for the Emulator Service.",
    version="1.0.0",
)


app.include_router(emulator_controller.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the Emulator Service REST API!"}


@app.on_event("shutdown")
def shutdown_event(): ...
