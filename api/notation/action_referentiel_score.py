from __future__ import annotations
from typing import Literal

from pydantic import BaseModel

ActionStatusSelectedValue = Literal[
    "faite", "programmee", "pas_faite", "non_concernee", ""
]


class ActionReferentielScore(BaseModel):
    action_id: str
    action_nomenclature_id: str
    action_status_valeur_selectionnee: ActionStatusSelectedValue
    points: float
    percentage: float
    potentiel: float
    referentiel_points: float
    referentiel_percentage: float
