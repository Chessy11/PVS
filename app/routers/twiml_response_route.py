from fastapi import APIRouter
from fastapi.responses import Response
from utils.twiml import generate_twiml

router = APIRouter()

@router.api_route("twiml/{code}", methods=["GET", "POST"])
async def get_twiml(code: str):
    twiml_response = generate_twiml(code)
    return Response(content=twiml_response, media_type="application/xml")