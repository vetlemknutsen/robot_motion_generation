from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Sequence

"""
Abstract base class for inverse kinematics solvers

Subclass this and implement solve() to add a new IK backend
See MoveItIKClient for an example
"""

class IKSolver(ABC):

    """
    Solve IK for the given end-effector pose
    Returns a dict mapping joint names to positions
    """
    @abstractmethod
    def solve(
        self,
        position: Sequence[float],
        orientation: Optional[Sequence[float]] = None,
        seed_state: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        ...

    def plan(
        self,
        position: Sequence[float],
        orientation: Optional[Sequence[float]] = None,
        seed_state: Optional[Dict[str, float]] = None,
    ) -> List[Dict[str, float]]:
        return [self.solve(position, orientation, seed_state)]
