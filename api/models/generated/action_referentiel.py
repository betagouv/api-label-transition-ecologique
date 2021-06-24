from datetime import date
from typing import List
from pydantic import BaseModel


class ActionReferentiel(BaseModel):
    id: str
    id_nomenclature: str
    nom: str
    description: str
    thematique_id: str
    actions: List[ActionReferentiel]
