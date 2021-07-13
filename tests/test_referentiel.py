from typing import List

import pytest

from api.models.generated.action_referentiel import ActionReferentiel
from api.notation.referentiel import Referentiel


def make_action_referentiel(
    id: str = "default_id",
    id_nomenclature: str = "",
    nom: str = "default_nom",
    description: str = "",
    thematique_id: str = "default_thematique_id",
    points: float = 42,
    actions: List[ActionReferentiel] = [],
):
    return ActionReferentiel(
        id=id,
        id_nomenclature=id_nomenclature,
        nom=nom,
        description=description,
        thematique_id=thematique_id,
        points=points,
        actions=actions,
    )


def test_referentiel_fails_when_wrong_root_action():
    with pytest.raises():
        referentiel = Referentiel(
            root_action=make_action_referentiel(id_nomenclature="not_empty")
        )


def test_referentiel_when_some_root_action_has_no_actions():
    root_action = make_action_referentiel(actions=[])
    referentiel = Referentiel(root_action)
    assert referentiel.backward == [()]
    assert referentiel.forward == [()]


def test_referentiel_when_root_action_has_one_level():
    action_1_1 = make_action_referentiel(id="ref__1", id_nomenclature="1", actions=[])
    root_action = make_action_referentiel(
        id="ref", id_nomenclature="", actions=[action_1_1], points=42
    )
    referentiel = Referentiel(root_action)

    assert referentiel.indices == [(), ("1",)]
    assert referentiel.backward == [("1",), ()]
    assert referentiel.forward == [(), ("1",)]
    assert referentiel.actions == {(): root_action, ("1",): action_1_1}
    assert referentiel.points == {(): 500, ("1",): 100}
    assert referentiel.percentages == {(): 1, ("1",): 0.2}
