import math

import pytest

from api.notation.economie_circulaire import Referentiel, Notation, Statut, referentiel_eci


@pytest.fixture
def referentiel() -> Referentiel:
    return referentiel_eci


@pytest.fixture
def notation(referentiel: Referentiel) -> Notation:
    return Notation(referentiel)


def test_referentiel(referentiel: Referentiel):
    # Compare hard a coded value
    math.isclose(notation.referentiel.points[('1', '1', '1')], 6.6)


def test_notation(notation: Notation):
    niveaux_of_1_1_1 = notation.referentiel.children(('1', '1', '1'))
    for niveau in niveaux_of_1_1_1:
        notation.set_statut(niveau, Statut.fait)

    notation.compute()
    point_of_1_1_1 = notation.referentiel.points[('1', '1', '1')]

    # test that orientation 1.1.1 have score 100% of the points
    assert math.isclose(notation.points[('1', '1', '1')], point_of_1_1_1)

    # test that orientation 1.1.2 points is 0
    assert notation.points[('1', '1', '2')] == 0

    # test that the point of root (that is the grand total) is equal to orientation 1.1.1
    assert math.isclose(notation.points[tuple()], point_of_1_1_1)
