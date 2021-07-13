from __future__ import annotations

from datetime import date
from typing import List, Literal
from pydantic import BaseModel


ActionStatusSelectedValue = Literal[
    "faite", "programmee", "pas_faite", "non_concernee", ""
]


class ActionStatus(BaseModel):
    action_id: str
    epci_id: str
    valeur_selectionnee: ActionStatusSelectedValue
