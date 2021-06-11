from pydantic import BaseModel

from api.models.pydantic.ademe_user_registration import AdemeUserRegistration


class UtilisateurConnecte(BaseModel):
    """"""
    ademe_user_id: str
    access_token: str
    refresh_token: str
    email: str
    nom: str
    prenom: str
