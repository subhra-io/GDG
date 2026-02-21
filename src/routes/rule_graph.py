"""Rule graph API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from src.core.database import get_db
from src.services.rule_graph import RuleGraphService

router = APIRouter(prefix="/api/v1/rules", tags=["rule-graph"])


class DependencyCreate(BaseModel):
    """Schema for creating a rule dependency."""
    depends_on_rule_id: str
    dependency_type: str  # 'requires', 'conflicts', 'extends'
    description: str = None


@router.get("/graph/{policy_id}")
def get_rule_graph(policy_id: str, db: Session = Depends(get_db)):
    """
    Get rule graph for a policy.
    
    Returns nodes and edges for visualization.
    """
    try:
        service = RuleGraphService(db)
        graph = service.get_rule_graph(policy_id)
        return graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get rule graph: {str(e)}")


@router.get("/conflicts/{policy_id}")
def detect_conflicts(policy_id: str, db: Session = Depends(get_db)):
    """
    Detect conflicting rules in a policy.
    
    Returns list of potential and explicit conflicts.
    """
    try:
        service = RuleGraphService(db)
        conflicts = service.detect_conflicts(policy_id)
        return {
            "conflicts": conflicts,
            "count": len(conflicts),
            "policy_id": policy_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect conflicts: {str(e)}")


@router.post("/{rule_id}/dependencies")
def add_dependency(
    rule_id: str,
    dependency: DependencyCreate,
    db: Session = Depends(get_db)
):
    """
    Add a dependency between rules.
    
    Dependency types:
    - requires: Rule requires another rule to be satisfied first
    - conflicts: Rule conflicts with another rule
    - extends: Rule extends/builds upon another rule
    """
    try:
        service = RuleGraphService(db)
        dep = service.add_dependency(
            rule_id=rule_id,
            depends_on_rule_id=dependency.depends_on_rule_id,
            dependency_type=dependency.dependency_type,
            description=dependency.description
        )
        return dep.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add dependency: {str(e)}")


@router.get("/cycles/{policy_id}")
def detect_cycles(policy_id: str, db: Session = Depends(get_db)):
    """
    Detect circular dependencies in rule graph.
    
    Returns list of cycles where each cycle is a list of rule IDs.
    """
    try:
        service = RuleGraphService(db)
        cycles = service.detect_circular_dependencies(policy_id)
        return {
            "cycles": cycles,
            "count": len(cycles),
            "policy_id": policy_id,
            "has_cycles": len(cycles) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect cycles: {str(e)}")


@router.get("/hierarchy/{policy_id}")
def get_rule_hierarchy(policy_id: str, db: Session = Depends(get_db)):
    """
    Get hierarchical structure of rules based on parent-child relationships.
    
    Returns tree structure with root rules and their children.
    """
    try:
        service = RuleGraphService(db)
        hierarchy = service.get_rule_hierarchy(policy_id)
        return hierarchy
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get hierarchy: {str(e)}")
