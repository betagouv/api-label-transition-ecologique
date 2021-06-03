import requests
from fastapi import APIRouter
from starlette.responses import JSONResponse

from api.config.configuration import AUTH_KEYCLOAK, AUTH_REALM, AUTH_CLIENT_ID, AUTH_SECRET
from api.models.pydantic.user_registration import UserRegistration

router = APIRouter(prefix='/v2/auth')

environment_domains = {
    "app": "https://territoiresentransitions.osc-fr1.scalingo.io",
    "sandbox": "https://sandboxterritoires.osc-fr1.scalingo.io",
    "local": "https://sandboxterritoires.osc-fr1.scalingo.io",
}

token_endpoint = f'{AUTH_KEYCLOAK}/auth/realms/{AUTH_REALM}/protocol/openid-connect/token'
auth_endpoint = f'{AUTH_KEYCLOAK}/auth/realms/{AUTH_REALM}/protocol/openid-connect/auth'


@router.post('/{environment}/register', response_class=JSONResponse)
async def register(environment: str, registration: UserRegistration):
    """Register a new user"""
    token_parameters = {
        'client_id': AUTH_CLIENT_ID,
        'client_secret': AUTH_SECRET,
        'grant_type': 'client_credentials',
    }
    token_response = requests.post(token_endpoint, data=token_parameters)
    token_json = token_response.json()
    access_token = token_json['access_token']

    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.post(auth_endpoint, json=registration.json(), headers=headers)
    return response.json()


@router.get('/{environment}/token', response_class=JSONResponse)
async def token(environment: str, code: str):
    """Returns a token from an code"""
    parameters = {
        'client_id': AUTH_CLIENT_ID,
        'client_secret': AUTH_SECRET,
        'grant_type': 'client_credentials',
        'code': code,
    }
    response = requests.post(token_endpoint, parameters)
    return response.json()
