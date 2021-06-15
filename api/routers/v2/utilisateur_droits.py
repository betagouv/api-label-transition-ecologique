from typing import List

from fastapi import APIRouter, HTTPException, Depends
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

from api.models.pydantic.utilisateur_connecte import UtilisateurConnecte
from api.models.tortoise.utilisateur_droits import UtilisateurDroits_Pydantic, UtilisateurDroits, \
    UtilisateurDroitsIn_Pydantic
from api.routers.dependencies.auth import get_user_from_header

router = APIRouter(prefix='/v2/utilisateur_droits')


@router.post("/", response_model=UtilisateurDroits_Pydantic)
async def write_droits(
        droits: UtilisateurDroitsIn_Pydantic,
        utilisateur: UtilisateurConnecte = Depends(get_user_from_header)
):
    if utilisateur.ademe_user_id != droits.ademe_user_id:
        raise HTTPException(status_code=401, detail="ademe_user_id mismatch")

    query = UtilisateurDroits.filter(ademe_user_id=droits.ademe_user_id, epci_id=droits.epci_id)

    if query.exists():
        await query.delete()

    droits_obj = await UtilisateurDroits.create(**droits.dict(exclude_unset=True))
    return await UtilisateurDroits_Pydantic.from_tortoise_orm(droits_obj)


@router.get(
    "/{ademe_user_id}", response_model=List[UtilisateurDroits_Pydantic],
    responses={404: {"model": HTTPNotFoundError}}
)
async def get_droits(ademe_user_id: str):
    query = UtilisateurDroits.filter(ademe_user_id=ademe_user_id)
    try:
        return await UtilisateurDroits_Pydantic.from_queryset(query)
    except DoesNotExist as error:
        raise HTTPException(status_code=404, detail=f"droits {ademe_user_id} not found")
