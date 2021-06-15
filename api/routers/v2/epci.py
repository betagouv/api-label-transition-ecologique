from typing import List

from fastapi import APIRouter, HTTPException, Depends
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

from api.models.tortoise.epci import Epci_Pydantic, Epci, EpciIn_Pydantic
from api.models.tortoise.utilisateur_droits import UtilisateurDroits_Pydantic
from api.routers.dependencies.auth import get_utilisateur_droits_from_header, can_write_epci

router = APIRouter(prefix='/v2/epci')


@router.post("/", response_model=Epci_Pydantic)
async def write_epci(
        epci: EpciIn_Pydantic,
        droits: List[UtilisateurDroits_Pydantic] = Depends(get_utilisateur_droits_from_header)
):
    if not can_write_epci(epci.uid, droits):
        raise HTTPException(status_code=401, detail=f"droits not found for epci {epci.uid}")

    query = Epci.filter(uid=epci.uid)

    if query.exists():
        await query.delete()

    epci_obj = await Epci.create(**epci.dict(exclude_unset=True))
    return await Epci_Pydantic.from_tortoise_orm(epci_obj)


@router.get("/all", response_model=List[Epci_Pydantic])
async def get_all_epci():
    query = Epci.all()
    return await Epci_Pydantic.from_queryset(query)


@router.get(
    "/{uid}", response_model=Epci_Pydantic,
    responses={404: {"model": HTTPNotFoundError}}
)
async def get_epci(uid: str):
    query = Epci.get(uid=uid)
    try:
        return await Epci_Pydantic.from_queryset_single(query)
    except DoesNotExist as error:
        raise HTTPException(status_code=404, detail=f"epci {uid} not found")
