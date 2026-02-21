# 🚀 Start Round 3 Implementation - Quick Guide

## 📋 Pre-Implementation Checklist

Before starting, ensure:
- [ ] Current code is committed to Git
- [ ] Backend and frontend are working
- [ ] Database is accessible
- [ ] You have 3-4 weeks available
- [ ] API keys are configured (for testing)

---

## 🎯 Week 1 - Day 1: Rule Graph Engine (Start Here!)

### Morning (4 hours): Database Schema

#### 1. Create Migration Script
```bash
touch scripts/migrate_rule_graph.py
```

```python
# scripts/migrate_rule_graph.py
"""Migration script for rule graph features."""

import psycopg2
from src.config.settings import settings

def migrate():
    conn = psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        database=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password
    )
    
    cursor = conn.cursor()
    
    # Add parent_rule_id to compliance_rules
    cursor.execute("""
        ALTER TABLE compliance_rules 
        ADD COLUMN IF NOT EXISTS parent_rule_id UUID REFERENCES compliance_rules(id);
    """)
    
    cursor.execute("""
        ALTER TABLE compliance_rules 
        ADD COLUMN IF NOT EXISTS precedence INTEGER DEFAULT 0;
    """)
    
    # Create rule_dependencies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rule_dependencies (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            rule_id UUID REFERENCES compliance_rules(id) ON DELETE CASCADE,
            depends_on_rule_id UUID REFERENCES compliance_rules(id) ON DELETE CASCADE,
            dependency_type VARCHAR(50) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(rule_id, depends_on_rule_id)
        );
    """)
    
    # Create index for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_rule_dependencies_rule_id 
        ON rule_dependencies(rule_id);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_rule_dependencies_depends_on 
        ON rule_dependencies(depends_on_rule_id);
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("✅ Rule graph migration completed!")

if __name__ == "__main__":
    migrate()
```

#### 2. Run Migration
```bash
python scripts/migrate_rule_graph.py
```

---

### Afternoon (4 hours): Backend Models & Service

#### 3. Create Rule Dependency Model
```bash
touch src/models/rule_dependency.py
```

```python
# src/models/rule_dependency.py
"""Rule dependency model for rule graph."""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base

class RuleDependency(Base):
    """Rule dependency for building rule graphs."""
    
    __tablename__ = "rule_dependencies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("compliance_rules.id", ondelete="CASCADE"), nullable=False)
    depends_on_rule_id = Column(UUID(as_uuid=True), ForeignKey("compliance_rules.id", ondelete="CASCADE"), nullable=False)
    dependency_type = Column(String(50), nullable=False)  # 'requires', 'conflicts', 'extends'
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rule = relationship("ComplianceRule", foreign_keys=[rule_id], backref="dependencies")
    depends_on_rule = relationship("ComplianceRule", foreign_keys=[depends_on_rule_id])
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "rule_id": str(self.rule_id),
            "depends_on_rule_id": str(self.depends_on_rule_id),
            "dependency_type": self.dependency_type,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
```

#### 4. Update ComplianceRule Model
```python
# Add to src/models/rule.py
from sqlalchemy import Column, Integer

# Add these columns to ComplianceRule class:
parent_rule_id = Column(UUID(as_uuid=True), ForeignKey("compliance_rules.id"))
precedence = Column(Integer, default=0)

# Add relationship
parent_rule = relationship("ComplianceRule", remote_side=[id], backref="child_rules")
```

#### 5. Create Rule Graph Service
```bash
touch src/services/rule_graph.py
```

```python
# src/services/rule_graph.py
"""Rule graph service for managing rule relationships."""

from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session
from src.models.rule import ComplianceRule
from src.models.rule_dependency import RuleDependency
from src.core.logging import get_logger

logger = get_logger(__name__)

class RuleGraphService:
    """Service for building and analyzing rule graphs."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_rule_graph(self, policy_id: str) -> Dict[str, Any]:
        """
        Get rule graph for a policy.
        
        Returns:
            Graph structure with nodes and edges
        """
        # Get all rules for policy
        rules = self.db.query(ComplianceRule).filter(
            ComplianceRule.policy_document_id == policy_id
        ).all()
        
        # Get all dependencies
        rule_ids = [str(rule.id) for rule in rules]
        dependencies = self.db.query(RuleDependency).filter(
            RuleDependency.rule_id.in_(rule_ids)
        ).all()
        
        # Build graph structure
        nodes = []
        for rule in rules:
            nodes.append({
                "id": str(rule.id),
                "label": rule.description[:50] + "..." if len(rule.description) > 50 else rule.description,
                "severity": rule.severity,
                "precedence": rule.precedence or 0,
                "type": "rule"
            })
        
        edges = []
        for dep in dependencies:
            edges.append({
                "id": str(dep.id),
                "source": str(dep.rule_id),
                "target": str(dep.depends_on_rule_id),
                "type": dep.dependency_type,
                "label": dep.dependency_type
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "policy_id": policy_id
        }
    
    def detect_conflicts(self, policy_id: str) -> List[Dict[str, Any]]:
        """Detect conflicting rules."""
        conflicts = []
        
        # Get all rules
        rules = self.db.query(ComplianceRule).filter(
            ComplianceRule.policy_document_id == policy_id
        ).all()
        
        # Simple conflict detection: same field, opposite operators
        for i, rule1 in enumerate(rules):
            for rule2 in rules[i+1:]:
                if self._rules_conflict(rule1, rule2):
                    conflicts.append({
                        "rule1_id": str(rule1.id),
                        "rule1_description": rule1.description,
                        "rule2_id": str(rule2.id),
                        "rule2_description": rule2.description,
                        "conflict_type": "operator_mismatch"
                    })
        
        return conflicts
    
    def _rules_conflict(self, rule1: ComplianceRule, rule2: ComplianceRule) -> bool:
        """Check if two rules conflict."""
        # Simplified conflict detection
        # In production, this would be more sophisticated
        return False  # Placeholder
    
    def add_dependency(
        self,
        rule_id: str,
        depends_on_rule_id: str,
        dependency_type: str,
        description: str = None
    ) -> RuleDependency:
        """Add a dependency between rules."""
        dependency = RuleDependency(
            rule_id=rule_id,
            depends_on_rule_id=depends_on_rule_id,
            dependency_type=dependency_type,
            description=description
        )
        
        self.db.add(dependency)
        self.db.commit()
        self.db.refresh(dependency)
        
        logger.info(
            "Rule dependency created",
            rule_id=rule_id,
            depends_on=depends_on_rule_id,
            type=dependency_type
        )
        
        return dependency
    
    def detect_circular_dependencies(self, policy_id: str) -> List[List[str]]:
        """Detect circular dependencies in rule graph."""
        # Build adjacency list
        rules = self.db.query(ComplianceRule).filter(
            ComplianceRule.policy_document_id == policy_id
        ).all()
        
        rule_ids = [str(rule.id) for rule in rules]
        dependencies = self.db.query(RuleDependency).filter(
            RuleDependency.rule_id.in_(rule_ids)
        ).all()
        
        graph = {rule_id: [] for rule_id in rule_ids}
        for dep in dependencies:
            graph[str(dep.rule_id)].append(str(dep.depends_on_rule_id))
        
        # DFS to detect cycles
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor, path.copy()):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                    return True
            
            rec_stack.remove(node)
            return False
        
        for rule_id in rule_ids:
            if rule_id not in visited:
                dfs(rule_id, [])
        
        return cycles
```

---

### Evening (2 hours): API Endpoints

#### 6. Create Rule Graph Routes
```bash
touch src/routes/rule_graph.py
```

```python
# src/routes/rule_graph.py
"""Rule graph API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from src.core.database import get_db
from src.services.rule_graph import RuleGraphService

router = APIRouter(prefix="/api/v1/rules", tags=["rule-graph"])

class DependencyCreate(BaseModel):
    depends_on_rule_id: str
    dependency_type: str
    description: str = None

@router.get("/graph/{policy_id}")
def get_rule_graph(policy_id: str, db: Session = Depends(get_db)):
    """Get rule graph for a policy."""
    service = RuleGraphService(db)
    return service.get_rule_graph(policy_id)

@router.get("/conflicts/{policy_id}")
def detect_conflicts(policy_id: str, db: Session = Depends(get_db)):
    """Detect conflicting rules in a policy."""
    service = RuleGraphService(db)
    conflicts = service.detect_conflicts(policy_id)
    return {"conflicts": conflicts, "count": len(conflicts)}

@router.post("/{rule_id}/dependencies")
def add_dependency(
    rule_id: str,
    dependency: DependencyCreate,
    db: Session = Depends(get_db)
):
    """Add a dependency between rules."""
    service = RuleGraphService(db)
    dep = service.add_dependency(
        rule_id=rule_id,
        depends_on_rule_id=dependency.depends_on_rule_id,
        dependency_type=dependency.dependency_type,
        description=dependency.description
    )
    return dep.to_dict()

@router.get("/cycles/{policy_id}")
def detect_cycles(policy_id: str, db: Session = Depends(get_db)):
    """Detect circular dependencies."""
    service = RuleGraphService(db)
    cycles = service.detect_circular_dependencies(policy_id)
    return {"cycles": cycles, "count": len(cycles)}
```

#### 7. Register Routes in main.py
```python
# Add to src/main.py
from src.routes.rule_graph import router as rule_graph_router

app.include_router(rule_graph_router)
```

---

## ✅ Day 1 Checklist

- [ ] Migration script created and run
- [ ] RuleDependency model created
- [ ] ComplianceRule model updated
- [ ] RuleGraphService implemented
- [ ] API endpoints created
- [ ] Routes registered in main.py
- [ ] Backend restarted and tested

---

## 🧪 Testing Day 1 Work

```bash
# Test rule graph endpoint
curl http://localhost:8000/api/v1/rules/graph/{policy_id}

# Test conflict detection
curl http://localhost:8000/api/v1/rules/conflicts/{policy_id}

# Test cycle detection
curl http://localhost:8000/api/v1/rules/cycles/{policy_id}
```

---

## ✅ Day 2: COMPLETE - Frontend Graph Visualization

Built:
- ✅ React Flow graph component
- ✅ Interactive node/edge visualization
- ✅ Conflict highlighting
- ✅ Dependency type coloring

## ✅ Day 3: COMPLETE - Advanced Graph Features

Built:
- ✅ Conflict highlighting with visual feedback
- ✅ Cycle detection with orange highlighting
- ✅ Interactive node details panel
- ✅ Multi-format export (PNG, SVG, JSON)
- ✅ Layout algorithms with smooth transitions
- ✅ Enhanced stats bar with conflict/cycle counts
- ✅ Control bar with all actions
- ✅ Conflict and cycle lists below graph

## 📅 Tomorrow (Day 4): Enhanced Reasoning Traces

You'll improve:
- Policy clause references in traces
- Page number extraction from PDFs
- Clause highlighting service
- Better UI integration
- Export to PDF functionality

---

## 💡 Tips for Success

1. **Commit often** - After each major step
2. **Test as you go** - Don't wait until the end
3. **Document changes** - Update README
4. **Ask for help** - If stuck, review the plan
5. **Stay focused** - One feature at a time

---

## 🚀 Ready to Start?

```bash
# 1. Create a new branch
git checkout -b feature/rule-graph-engine

# 2. Start with migration
python scripts/migrate_rule_graph.py

# 3. Create models and services
# Follow the steps above

# 4. Test and commit
git add .
git commit -m "feat: implement rule graph engine backend"
```

---

**Let's build this! Day 1 starts now! 💪**
