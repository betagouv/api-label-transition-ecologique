from enum import Enum, unique
from typing import Tuple, Dict

from api.data.generated.referentiels import actions
from api.models.generated.action_referentiel import ActionReferentiel


class Referentiel:
    """Build referentiel table."""

    def __init__(self, root_action: ActionReferentiel):
        self.root_action: ActionReferentiel = root_action
        self.points: Dict[Tuple, float] = {}
        self.percentages: Dict[Tuple, float] = {}
        self._build_points()
        self._build_percentages()

    def _build_points(self):
        def add_action(action: ActionReferentiel):
            index = tuple([element for element in action.id_nomenclature.split('.') if element])
            if len(index) == 0:
                # référentiel
                weight = 500
            elif len(index) == 1:
                # axe
                weight = 100
            else:
                # orientation, niveau, tache
                weight = max(action.points, 0) * (self.points[index[:-1]] / 100)
            self.points[index] = weight
            for action in action.actions:
                add_action(action)

        add_action(self.root_action)

    def _build_percentages(self):
        for index in self.points.keys():
            if len(index) > 0:
                p = self.points[index]
                if p == 0:
                    self.percentages[index] = 0
                else:
                    self.percentages[index] = (self.points[index] / self.points[index[:-1]]) * 100

        self.percentages[tuple()] = 100


@unique
class Statut(Enum):
    pas_fait = 0
    fait = 1
    pas_concerne = 2
    vide = 3


class Notation:
    """Permet de noter une collectivité"""

    def __init__(self, referentiel: Referentiel) -> None:
        self.referentiel = referentiel
        self.points: Dict[Tuple, float] = referentiel.points.copy()
        self.statuts: Dict[Tuple, Statut] = {index: Statut.pas_fait for index in self.points.keys()}

        indices = self.points.keys()
        self.forward = sorted(indices, key=lambda i: len(i))
        self.backward = sorted(indices, key=lambda i: len(i), reverse=True)
        pass



if __name__ == '__main__':
    eci = Referentiel(actions[-1])
    notation = Notation(eci)
