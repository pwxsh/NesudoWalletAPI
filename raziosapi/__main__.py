import asyncio

import uvicorn
from fastapi import FastAPI

from raziosapi.database.core import (
    create_models,
    drop_models
)
from raziosapi.routers import (
    wallet_router,
    transfers_router,
    cheques_router,
    invoices_router
)


app = FastAPI(debug=True)

app.include_router(wallet_router)
app.include_router(transfers_router)
app.include_router(cheques_router)
app.include_router(invoices_router)

if __name__ == "__main__":
    uvicorn.run("raziosapi.__main__:app", host="localhost", port=8080, reload=True)
