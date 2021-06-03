import requests
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse

from api.config.configuration import AUTH_KEYCLOAK, AUTH_REALM, AUTH_CLIENT_ID, AUTH_SECRET

router = APIRouter(prefix='/v2/auth')

environment_domains = {
    "app": "https://territoiresentransitions.osc-fr1.scalingo.io",
    "sandbox": "https://sandboxterritoires.osc-fr1.scalingo.io",
    "local": "https://sandboxterritoires.osc-fr1.scalingo.io",
}


@router.post('/{environment}/register', response_class=HTMLResponse)
async def register(environment: str):
    pass


@router.get('/{environment}/redirect', response_class=JSONResponse)
async def redirect_handler(environment: str, code: str):
    print(f'got {code}')
    token_endpoint = f'{AUTH_KEYCLOAK}/auth/realms/{AUTH_REALM}/protocol/openid-connect/token'
    response = requests.post(token_endpoint, client_id=AUTH_CLIENT_ID, client_secret=AUTH_SECRET, code=code)
    print(response.text)
    return response.text
