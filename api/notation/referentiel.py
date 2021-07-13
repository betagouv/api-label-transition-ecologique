from __future__ import annotations

from typing import Tuple, Dict, List

from api.models.generated.action_referentiel import ActionReferentiel


class Referentiel:
    """Referentiel.

    Takes the root action of a referentiel and compute tables and indices.
    - points are used by Notation to compute scores.
    - percentages are used to display/test computation
    - actions allows for index to

    ## Indices
    indices, forward and backward are indices list for iterating either
    in no particular order, forward (from root to tâches) or backward (tâches to root) respectively.
    """

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
        """Returns the children indices"""
        return [index for index in self.indices if index[:-1] == parent and len(index)]

    def siblings(self, index: tuple) -> List[tuple]:
        """Returns the index siblings including index"""
        parent = index[:-1]
        return self.children(parent)

    def __build_indices(self):
        """Build all indices lists"""
        self.indices: List[Tuple] = []

        def add_action(action: ActionReferentiel):
            index = tuple(
                [element for element in action.id_nomenclature.split(".") if element]
            )
            self.indices.append(index)
            self.actions[index] = action

            for action in action.actions:
                add_action(action)

        add_action(self.root_action)

        self.forward: List[Tuple] = sorted(self.indices, key=lambda i: len(i))
        self.backward: List[Tuple] = sorted(
            self.indices, key=lambda i: len(i), reverse=True
        )

    def __build_points(self):
        """Build points
        A référentiel is worth 500 points thus if every actions had a been done
        perfectly a collectivité would obtain 500 points.

        Axes and orientations points are hardcoded for now as the markdown is
        not properly defined for now.
        """
        for index in self.indices:
            if len(index) == 0:
                # référentiel
                points = 500  # TODO: this should not be hard-coded
            elif len(index) == 1:
                # axe
                points = 100
            else:
                # orientation, niveau, tache
                points = max(self.actions[index].points, 0) * (
                    self.points[index[:-1]] / 100
                )
            self.points[index] = points

    def __build_percentages(self):
        """Build percentages

        Percentages are relative to parents. If an action had 4 children, each would be .25 that is 25%"""
        for index in self.points.keys():
            if len(index) > 0:
                p = self.points[index]
                if p == 0:
                    self.percentages[index] = 0
                else:
                    self.percentages[index] = (
                        self.points[index] / self.points[index[:-1]]
                    )
        self.percentages[tuple()] = 100
