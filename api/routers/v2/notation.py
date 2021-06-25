from typing import List

from fastapi import APIRouter

from api.data.generated.referentiels import actions
from api.models.generated.action_referentiel_score import ActionReferentielScore
from api.models.tortoise.action_status import ActionStatus_Pydantic, ActionStatus
from api.notation.economie_circulaire import Referentiel, Notation, Statut

router = APIRouter(prefix='/v2/notation')

referentiel_eci = Referentiel(actions[-1])


@router.get("/eci/{epci_id}/all", response_model=List[ActionReferentielScore])
async def get_eci_scores(epci_id: str):
    query = ActionStatus.filter(epci_id=epci_id, latest=True)
    status: List[ActionStatus] = await ActionStatus_Pydantic.from_queryset(query)
    notation = Notation(referentiel_eci)

    for s in status:
        if s.action_id.startswith('economie_circulaire'):
            index = tuple(s.action_id.split('__')[-1].split('.'))
            notation.set_statut(index, Statut.from_avancement(s.avancement))

    return notation.scores()
