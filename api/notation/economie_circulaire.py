from __future__ import annotations

from enum import Enum, unique
from typing import Tuple, Dict, List

from pydantic import BaseModel

from api.data.generated.referentiels import actions
from api.models.generated.action_referentiel import ActionReferentiel


class Referentiel:
    """Build referentiel table."""

    def __init__(self, root_action: ActionReferentiel):
        self.root_action: ActionReferentiel = root_action
        self.points: Dict[Tuple, float] = {}
        self.percentages: Dict[Tuple, float] = {}
        self.actions: Dict[Tuple, ActionReferentiel] = {}
        self.indices: List[Tuple]
        self.forward: List[Tuple]
        self.backward: List[Tuple]
        self.__build_indices()
        self.__build_points()
        self.__build_percentages()

    def children(self, parent: tuple) -> List[tuple]:
        return [index for index in self.indices if index[:-1] == parent and len(index)]

    def siblings(self, index: tuple) -> List[tuple]:
        parent = index[:-1]
        return self.children(parent)

    def __build_indices(self):
        self.indices: List[Tuple] = []

        def add_action(action: ActionReferentiel):
            index = tuple([element for element in action.id_nomenclature.split('.') if element])
            self.indices.append(index)
            self.actions[index] = action

            for action in action.actions:
                add_action(action)

        add_action(self.root_action)

        self.forward: List[Tuple] = sorted(self.indices, key=lambda i: len(i))
        self.backward: List[Tuple] = sorted(self.indices, key=lambda i: len(i), reverse=True)

    def __build_points(self):
        for index in self.indices:
            if len(index) == 0:
                # référentiel
                points = 500
            elif len(index) == 1:
                # axe
                points = 100
            else:
                # orientation, niveau, tache
                points = max(self.actions[index].points, 0) * (self.points[index[:-1]] / 100)
            self.points[index] = points

    def __build_percentages(self):
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

    def __str__(self):
        if self == Statut.pas_fait:
            return 'pas_faite'
        elif self == Statut.fait:
            return 'faite'
        elif self == Statut.pas_concerne:
            return 'pas_concernee'
        return 'vide'


class Score(BaseModel):
    action_id: str
    action_nomenclature_id: str
    status: str
    points: float
    potentiel: float
    referentiel_points: float
    referentiel_percentage: float


class Notation:
    """Permet de noter une collectivité"""

    def __init__(self, referentiel: Referentiel) -> None:
        self.referentiel = referentiel
        self.potentiels: Dict[Tuple, float] = {}
        self.points: Dict[Tuple, float] = {}
        self.statuts: Dict[Tuple, Statut] = {}
        self.dirty: bool = False
        self.reset()

    def reset(self):
        self.potentiels: Dict[Tuple, float] = self.referentiel.points.copy()
        self.statuts: Dict[Tuple, Statut] = {index: Statut.vide for index in self.referentiel.indices}
        self.points: Dict[Tuple, float] = {index: .0 for index in self.referentiel.indices}
        self.dirty: bool = False

    def set_statut(self, index: Tuple, statut: Statut):
        """Set the status of an action"""
        self.dirty = True
        self.statuts[index] = statut

    def compute(self):
        self.__propagate_statuts()
        self.__compute_potentiels()
        self.__compute_points()
        self.dirty = False

    def scores(self):
        if self.dirty:
            self.compute()

        return [
            Score(
                action_id=self.referentiel.actions[index].id,
                action_nomenclature_id=self.referentiel.actions[index].id_nomenclature,
                status=str(self.statuts[index]),
                points=self.points[index],
                potentiel=self.potentiels[index],
                referentiel_points=self.referentiel.points[index],
                referentiel_percentage=self.referentiel.percentages[index],
            )
            for index in self.referentiel.indices if len(index)
        ]

    def __propagate_statuts(self):
        """Propagate `statuts` in the tree so there is no more `vide`"""

        def compute_parent_statut(chidren_statuts: List[Statut]) -> Statut:
            """parent status from its children"""
            if chidren_statuts.count(Statut.pas_concerne) == len(chidren_statuts):
                return Statut.pas_concerne
            elif chidren_statuts.count(Statut.fait) + chidren_statuts.count(Statut.pas_concerne) \
                    == len(chidren_statuts):
                return Statut.fait
            return Statut.pas_fait

        # forward propagation
        for index in self.referentiel.forward:
            if len(index) == 0:
                continue
            parent_statut = self.statuts[index[:-1]]
            if parent_statut != Statut.vide:
                self.statuts[index] = parent_statut

        # backward propagation
        for index in self.referentiel.backward:
            if self.statuts[index] != Statut.vide:
                continue
            children = self.referentiel.children(index)
            if children:
                self.statuts[index] = compute_parent_statut([self.statuts[child] for child in children])

    def __compute_potentiels(self):
        """Redistribute `points` of actions with a `statuts non concerné`"""
        for index in self.referentiel.backward:
            children = self.referentiel.children(index)
            children_statuts = [self.statuts[child] for child in children]
            exclusions = children_statuts.count(Statut.pas_concerne)

            if exclusions == 0:
                continue
            elif exclusions == len(children):
                for child in children:
                    self.potentiels[child] = .0
            else:
                excluded = sum([self.referentiel.points[child] for child in children if
                                self.statuts[child] == Statut.pas_concerne])
                redistribution = excluded / (len(children) - exclusions)

                for child in children:
                    if self.statuts[child] == Statut.pas_concerne:
                        self.potentiels[child] = .0
                    else:
                        self.potentiels[child] += redistribution

    def __compute_points(self):
        # first pass
        for index in self.referentiel.indices:
            progress = 1.0 if self.statuts[index] == Statut.fait else .0
            self.points[index] = progress * self.potentiels[index]

        # second pass
        for index in self.referentiel.backward:
            children = self.referentiel.children(index)
            if children:
                self.points[index] = sum([self.points[child] for child in children])


if __name__ == '__main__':
    eci = Referentiel(actions[-1])
    notation = Notation(eci)
    notation.compute()

    notation = Notation(eci)
    notation.set_statut(('1', '1', '1', '1'), Statut.fait)
    notation.set_statut(('1', '1', '1', '2'), Statut.fait)
    notation.set_statut(('1', '1', '1', '3'), Statut.fait)
    notation.set_statut(('1', '1', '1', '4'), Statut.fait)
    notation.set_statut(('1', '1', '1', '5'), Statut.fait)
    notation.compute()

    notation = Notation(eci)
    notation.set_statut(('1', '1', '1', '1'), Statut.pas_concerne)
    notation.set_statut(('1', '1', '1', '2'), Statut.pas_concerne)
    notation.set_statut(('1', '1', '1', '3'), Statut.pas_concerne)
    notation.set_statut(('1', '1', '1', '4'), Statut.pas_concerne)
    notation.set_statut(('1', '1', '1', '5'), Statut.pas_concerne)
    notation.compute()

    notation = Notation(eci)
    notation.set_statut(('1', '1', '1', '1'), Statut.fait)
    notation.set_statut(('1', '1', '1', '2'), Statut.fait)
    notation.set_statut(('1', '1', '1', '3'), Statut.pas_concerne)
    notation.set_statut(('1', '1', '1', '4'), Statut.pas_concerne)
    notation.set_statut(('1', '1', '1', '5'), Statut.pas_concerne)

    notation.set_statut(('1', '1', '2'), Statut.fait)
    notation.set_statut(('2',), Statut.pas_concerne)
    notation.compute()
    pass
