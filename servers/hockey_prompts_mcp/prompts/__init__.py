"""
Hockey Practice Planning Prompt Workflows

This module contains the workflow implementations for hockey practice planning
and review processes.
"""

from .practice_planning import PracticePlanningWorkflow
from .practice_review import PracticeReviewWorkflow

__all__ = [
    'PracticePlanningWorkflow',
    'PracticeReviewWorkflow'
]