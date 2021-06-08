from pydantic import BaseModel

from api.models.pydantic.ademe_user_registration import AdemeUserRegistration


class UtilisateurConnecte(BaseModel):
    """User data sent to the client on login and on registration"""
    ademe_user_id: str
    access_token: str
    email: str
    nom: str
    prenom: str