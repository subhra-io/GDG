"""Rule graph service for managing rule relationships."""

from typing import List, Dict, Any, Set, Tuple
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
        
        Args:
            policy_id: Policy document ID
            
        Returns:
            Graph structure with nodes and edges
        """
        # Get all rules for policy
        rules = self.db.query(ComplianceRule).filter(
            ComplianceRule.policy_document_id == policy_id,
            ComplianceRule.is_active == True
        ).all()
        
        if not rules:
            return {
                "nodes": [],
                "edges": [],
                "policy_id": policy_id,
                "stats": {
                    "total_rules": 0,
                    "total_dependencies": 0
                }
            }
        
        # Get all dependencies
        rule_ids = [str(rule.id) for rule in rules]
        dependencies = self.db.query(RuleDependency).filter(
            RuleDependency.rule_id.in_(rule_ids)
        ).all()
        
        # Build graph structure
        nodes = []
        for rule in rules:
            # Truncate description for display
            label = rule.description[:60] + "..." if len(rule.description) > 60 else rule.description
            
            nodes.append({
                "id": str(rule.id),
                "label": label,
                "description": rule.description,
                "severity": rule.severity.value if hasattr(rule.severity, 'value') else rule.severity,
                "precedence": int(rule.precedence) if rule.precedence else 0,
                "is_active": rule.is_active,
                "parent_rule_id": str(rule.parent_rule_id) if rule.parent_rule_id else None,
                "type": "rule"
            })
        
        edges = []
        for dep in dependencies:
            edges.append({
                "id": str(dep.id),
                "source": str(dep.rule_id),
                "target": str(dep.depends_on_rule_id),
                "type": dep.dependency_type,
                "label": dep.dependency_type.replace('_', ' ').title(),
                "description": dep.description
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "policy_id": policy_id,
            "stats": {
                "total_rules": len(nodes),
                "total_dependencies": len(edges),
                "by_severity": self._count_by_severity(rules)
            }
        }
    
    def _count_by_severity(self, rules: List[ComplianceRule]) -> Dict[str, int]:
        """Count rules by severity."""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for rule in rules:
            severity = rule.severity.value if hasattr(rule.severity, 'value') else rule.severity
            if severity in counts:
                counts[severity] += 1
        return counts
    
    def detect_conflicts(self, policy_id: str) -> List[Dict[str, Any]]:
        """
        Detect conflicting rules.
        
        Args:
            policy_id: Policy document ID
            
        Returns:
            List of conflicts
        """
        conflicts = []
        
        # Get all rules
        rules = self.db.query(ComplianceRule).filter(
            ComplianceRule.policy_document_id == policy_id,
            ComplianceRule.is_active == True
        ).all()
        
        # Check for explicit conflict dependencies
        rule_ids = [str(rule.id) for rule in rules]
        conflict_deps = self.db.query(RuleDependency).filter(
            RuleDependency.rule_id.in_(rule_ids),
            RuleDependency.dependency_type == 'conflicts'
        ).all()
        
        for dep in conflict_deps:
            rule1 = next((r for r in rules if str(r.id) == str(dep.rule_id)), None)
            rule2 = next((r for r in rules if str(r.id) == str(dep.depends_on_rule_id)), None)
            
            if rule1 and rule2:
                conflicts.append({
                    "rule1_id": str(rule1.id),
                    "rule1_description": rule1.description,
                    "rule1_severity": rule1.severity.value if hasattr(rule1.severity, 'value') else rule1.severity,
                    "rule2_id": str(rule2.id),
                    "rule2_description": rule2.description,
                    "rule2_severity": rule2.severity.value if hasattr(rule2.severity, 'value') else rule2.severity,
                    "conflict_type": "explicit",
                    "description": dep.description
                })
        
        # Simple heuristic conflict detection
        # Check for rules with same field but opposite operators
        for i, rule1 in enumerate(rules):
            for rule2 in rules[i+1:]:
                if self._rules_potentially_conflict(rule1, rule2):
                    conflicts.append({
                        "rule1_id": str(rule1.id),
                        "rule1_description": rule1.description,
                        "rule1_severity": rule1.severity.value if hasattr(rule1.severity, 'value') else rule1.severity,
                        "rule2_id": str(rule2.id),
                        "rule2_description": rule2.description,
                        "rule2_severity": rule2.severity.value if hasattr(rule2.severity, 'value') else rule2.severity,
                        "conflict_type": "potential",
                        "description": "Rules may have conflicting conditions"
                    })
        
        return conflicts
    
    def _rules_potentially_conflict(self, rule1: ComplianceRule, rule2: ComplianceRule) -> bool:
        """
        Check if two rules potentially conflict.
        
        This is a simplified heuristic - in production, this would be more sophisticated.
        """
        # Check if both rules have validation logic
        if not rule1.validation_logic or not rule2.validation_logic:
            return False
        
        # Check if they target the same field
        logic1 = rule1.validation_logic
        logic2 = rule2.validation_logic
        
        field1 = logic1.get('field') if isinstance(logic1, dict) else None
        field2 = logic2.get('field') if isinstance(logic2, dict) else None
        
        if field1 and field2 and field1 == field2:
            # Check for opposite operators
            op1 = logic1.get('operator', '')
            op2 = logic2.get('operator', '')
            
            opposite_pairs = [
                ('greater_than', 'less_than'),
                ('equals', 'not_equals'),
                ('contains', 'not_contains')
            ]
            
            for pair in opposite_pairs:
                if (op1 == pair[0] and op2 == pair[1]) or (op1 == pair[1] and op2 == pair[0]):
                    return True
        
        return False
    
    def add_dependency(
        self,
        rule_id: str,
        depends_on_rule_id: str,
        dependency_type: str,
        description: str = None
    ) -> RuleDependency:
        """
        Add a dependency between rules.
        
        Args:
            rule_id: Source rule ID
            depends_on_rule_id: Target rule ID
            dependency_type: Type of dependency ('requires', 'conflicts', 'extends')
            description: Optional description
            
        Returns:
            Created dependency
        """
        # Validate rules exist
        rule = self.db.query(ComplianceRule).filter(ComplianceRule.id == rule_id).first()
        depends_on = self.db.query(ComplianceRule).filter(ComplianceRule.id == depends_on_rule_id).first()
        
        if not rule or not depends_on:
            raise ValueError("One or both rules not found")
        
        # Check if dependency already exists
        existing = self.db.query(RuleDependency).filter(
            RuleDependency.rule_id == rule_id,
            RuleDependency.depends_on_rule_id == depends_on_rule_id
        ).first()
        
        if existing:
            # Update existing
            existing.dependency_type = dependency_type
            existing.description = description
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        # Create new dependency
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
        """
        Detect circular dependencies in rule graph.
        
        Args:
            policy_id: Policy document ID
            
        Returns:
            List of cycles (each cycle is a list of rule IDs)
        """
        # Build adjacency list
        rules = self.db.query(ComplianceRule).filter(
            ComplianceRule.policy_document_id == policy_id,
            ComplianceRule.is_active == True
        ).all()
        
        rule_ids = [str(rule.id) for rule in rules]
        dependencies = self.db.query(RuleDependency).filter(
            RuleDependency.rule_id.in_(rule_ids),
            RuleDependency.dependency_type == 'requires'  # Only check 'requires' for cycles
        ).all()
        
        # Build graph
        graph = {rule_id: [] for rule_id in rule_ids}
        for dep in dependencies:
            graph[str(dep.rule_id)].append(str(dep.depends_on_rule_id))
        
        # DFS to detect cycles
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> bool:
            """Depth-first search to detect cycles."""
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
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                    return True
            
            rec_stack.remove(node)
            return False
        
        for rule_id in rule_ids:
            if rule_id not in visited:
                dfs(rule_id, [])
        
        return cycles
    
    def get_rule_hierarchy(self, policy_id: str) -> Dict[str, Any]:
        """
        Get hierarchical structure of rules based on parent-child relationships.
        
        Args:
            policy_id: Policy document ID
            
        Returns:
            Hierarchical tree structure
        """
        rules = self.db.query(ComplianceRule).filter(
            ComplianceRule.policy_document_id == policy_id,
            ComplianceRule.is_active == True
        ).all()
        
        # Build tree structure
        root_rules = [r for r in rules if not r.parent_rule_id]
        
        def build_tree(rule: ComplianceRule) -> Dict[str, Any]:
            children = [r for r in rules if r.parent_rule_id == rule.id]
            return {
                "id": str(rule.id),
                "description": rule.description,
                "severity": rule.severity.value if hasattr(rule.severity, 'value') else rule.severity,
                "precedence": int(rule.precedence) if rule.precedence else 0,
                "children": [build_tree(child) for child in sorted(children, key=lambda x: int(x.precedence) if x.precedence else 0)]
            }
        
        return {
            "policy_id": policy_id,
            "tree": [build_tree(rule) for rule in sorted(root_rules, key=lambda x: int(x.precedence) if x.precedence else 0)]
        }
