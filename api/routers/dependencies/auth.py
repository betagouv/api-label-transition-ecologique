from typing import List

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from starlette import status
from tortoise.exceptions import DoesNotExist

from api.config.configuration import AUTH_DISABLED_DUMMY_USER
from api.models.pydantic.utilisateur_connecte import UtilisateurConnecte
from api.models.tortoise.utilisateur_droits import UtilisateurDroits_Pydantic, UtilisateurDroits
from api.routers.v2.auth import token_endpoint

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_endpoint)


async def get_user_from_header(token: str = Depends(oauth2_scheme)) -> UtilisateurConnecte:
    """Retrieve user info from the token."""
    if AUTH_DISABLED_DUMMY_USER:
        return UtilisateurConnecte(
            ademe_user_id='dummy',
            prenom='Dummy',
            nom='Territoires en Transitions',
            email='dummy@territoiresentransitions.fr',
            access_token=token,
            refresh_token=''
        )

    try:
        # fixme: both jwt and jose libraries fail at verifying access token using keycloak's JWKs
        payload = jwt.decode(token, options={"verify_signature": False})

        user = UtilisateurConnecte(
            ademe_user_id=payload.get('sub', ''),
            prenom=payload.get('given_name', ''),
            nom=payload.get('family_name', ''),
            email=payload.get('email', ''),
            access_token=token,
            refresh_token=''
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_utilisateur_droits_from_header(
        utilisateur: UtilisateurConnecte = Depends(get_user_from_header)
) -> List[UtilisateurDroits_Pydantic]:
    """Retrieve the token bearer list of droits"""
    ademe_user_id = utilisateur.ademe_user_id
    query = UtilisateurDroits.filter(ademe_user_id=ademe_user_id)
    try:
        return await UtilisateurDroits_Pydantic.from_queryset(query)
    except DoesNotExist as error:
        raise HTTPException(status_code=401, detail=f"{ademe_user_id} droits not found")


def can_write_epci(epci_id: str, droits: List[UtilisateurDroits_Pydantic]) -> bool:
    """Returns true if there is a match in a list of droits for epci_id"""
    return bool([droit for droit in droits if droit.epci_id == epci_id and droit.ecriture])



