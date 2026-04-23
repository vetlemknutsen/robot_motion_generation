from abc import ABC, abstractmethod
from typing import Dict, Optional, Sequence

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

    def try_solve(
        self,
        position: Sequence[float],
        orientation: Optional[Sequence[float]] = None,
        seed_state: Optional[Dict[str, float]] = None,
    ) -> Optional[Dict[str, float]]:
        try:
            return self.solve(position, orientation, seed_state)
        except RuntimeError as e:
            print(f"IK solver error: {e}")
            return None
