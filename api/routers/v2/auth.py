import requests
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from api.config.configuration import AUTH_KEYCLOAK, AUTH_REALM, AUTH_CLIENT_ID

router = APIRouter(prefix='/v2/auth')

environment_domains = {
    "app": "https://territoiresentransitions.osc-fr1.scalingo.io",
    "sandbox": "https://sandboxterritoires.osc-fr1.scalingo.io",
    "local": "https://sandboxterritoires.osc-fr1.scalingo.io",
}


@router.post('/{environment}/register', response_class=HTMLResponse)
async def register(environment: str):
    pass


@router.get('/{environment}/login', response_class=HTMLResponse)
async def login_form(environment: str):
    """Forward the login form from keycloak"""
    redirect_domain = environment_domains[environment]
    form_url = f'{AUTH_KEYCLOAK}/auth/realms/{AUTH_REALM}/protocol/openid-connect/auth'
    parameters = {
        'client_id': AUTH_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': f'{redirect_domain}/v2/auth/{environment}/redirect'
    }
    response = requests.post(form_url, data=parameters)
    return response.text


@router.get('{environment}/redirect', response_class=HTMLResponse)
async def redirect_handler(environment: str, code: str):
    print(f'got {code}')
    token_endpoint = f'{AUTH_KEYCLOAK}/auth/realms/{AUTH_REALM}/protocol/openid-connect/token'
    
