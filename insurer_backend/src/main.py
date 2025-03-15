from fastapi import FastAPI

import clients.db_client as db_client
from config.db_config import engine

from handlers.ping import router as handle_ping
from handlers.v1_add_schema import router as handle_v1_add_scheme
from handlers.v1_add_schema import router as handle_v1_add_scheme_csv
from handlers.v1_icp_address import router as handle_v1_icp_address_get
from handlers.v1_add_user import router as handle_v1_add_user
from handlers.v1_authorize import router as handle_v1_authorize
from handlers.v1_balance import router as handle_v1_balance_request
from handlers.v1_operations import router as handle_v1_operations
from handlers.v1_register import router as handle_v1_register
from handlers.v1_schema import router as handle_v1_schema
from handlers.v1_schemas import router as handle_v1_schemas
from handlers.v1_update_user import router as handle_v1_update_user
from handlers.v1_user import router as handle_v1_user
from handlers.v1_users import router as handle_v1_users_get
from handlers.v1_withdraw import router as handle_v1_withdraw_post
from handlers.v1_check_sum import router as handle_v1_check_sum

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

db_client.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(handle_ping)
app.include_router(handle_v1_add_scheme)
app.include_router(handle_v1_add_scheme_csv)
app.include_router(handle_v1_icp_address_get)
app.include_router(handle_v1_add_user)
app.include_router(handle_v1_authorize)
app.include_router(handle_v1_balance_request)
app.include_router(handle_v1_operations)
app.include_router(handle_v1_register)
app.include_router(handle_v1_schema)
app.include_router(handle_v1_schemas)
app.include_router(handle_v1_update_user)
app.include_router(handle_v1_user)
app.include_router(handle_v1_users_get)
app.include_router(handle_v1_withdraw_post)
app.include_router(handle_v1_check_sum)
