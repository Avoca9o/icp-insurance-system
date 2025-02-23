from fastapi import APIRouter
from fastapi.responses import JSONResponse

from clients import icp_client

from pydantic import BaseModel

router = APIRouter()

icp = icp_client.ICPClient()


class WithdrawRequest(BaseModel):
    company: str

    def check_validity(self):
        if self.company is None or len(self.company) == 0:
            raise ValueError("Company name cannot be empty")


@router.post("/v1/withdraw")
def handle_v1_withdraw_post(req: WithdrawRequest):
    try:
        req.check_validity()
        # TODO: check company's number of clients, if there're some of them there cannot be an opportunity to withdraw
        icp.withdraw(req.company)
        return JSONResponse(content=None, status_code=200)
    except ValueError as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)