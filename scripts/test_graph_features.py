"""Script to test rule graph features by adding dependencies and conflicts."""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
POLICY_ID = "f7e759f0-240c-4233-877c-2686d39d9f36"

def get_rules():
    """Get all rules for the policy."""
    response = requests.get(f"{BASE_URL}/policies/{POLICY_ID}/rules")
    return response.json()

def add_dependency(rule_id, depends_on_rule_id, dependency_type, description):
    """Add a dependency between rules."""
    response = requests.post(
        f"{BASE_URL}/rules/{rule_id}/dependencies",
        json={
            "depends_on_rule_id": depends_on_rule_id,
            "dependency_type": dependency_type,
            "description": description
        }
    )
    return response.json()

def main():
    print("🔍 Fetching rules...")
    rules = get_rules()
    
    if len(rules) < 3:
        print("❌ Need at least 3 rules to create dependencies")
        return
    
    print(f"✅ Found {len(rules)} rules")
    
    # Get rule IDs
    rule1_id = rules[0]['id']  # Transactions over $10,000 (high)
    rule2_id = rules[1]['id']  # Wire transfers (critical)
    rule3_id = rules[2]['id']  # Cash transactions (medium)
    
    print(f"\n📋 Rules:")
    print(f"  Rule 1: {rules[0]['description']} ({rules[0]['severity']})")
    print(f"  Rule 2: {rules[1]['description']} ({rules[1]['severity']})")
    print(f"  Rule 3: {rules[2]['description']} ({rules[2]['severity']})")
    
    # Add dependencies
    print("\n🔗 Adding dependencies...")
    
    # Rule 2 requires Rule 1 (wire transfers require general transaction verification)
    dep1 = add_dependency(
        rule2_id,
        rule1_id,
        "requires",
        "Wire transfer checks require basic transaction verification first"
    )
    print(f"  ✅ Added: Rule 2 requires Rule 1")
    
    # Rule 3 extends Rule 1 (cash transactions are a type of transaction)
    dep2 = add_dependency(
        rule3_id,
        rule1_id,
        "extends",
        "Cash transaction rules extend general transaction rules"
    )
    print(f"  ✅ Added: Rule 3 extends Rule 1")
    
    # Rule 2 conflicts with Rule 3 (wire vs cash - different handling)
    dep3 = add_dependency(
        rule2_id,
        rule3_id,
        "conflicts",
        "Wire transfers and cash transactions have conflicting documentation requirements"
    )
    print(f"  ✅ Added: Rule 2 conflicts with Rule 3")
    
    # Verify graph
    print("\n📊 Verifying graph...")
    graph_response = requests.get(f"{BASE_URL}/rules/graph/{POLICY_ID}")
    graph = graph_response.json()
    
    print(f"  Nodes: {graph['stats']['total_rules']}")
    print(f"  Edges: {graph['stats']['total_dependencies']}")
    
    # Check conflicts
    conflicts_response = requests.get(f"{BASE_URL}/rules/conflicts/{POLICY_ID}")
    conflicts = conflicts_response.json()
    print(f"  Conflicts: {conflicts['count']}")
    
    # Check cycles
    cycles_response = requests.get(f"{BASE_URL}/rules/cycles/{POLICY_ID}")
    cycles = cycles_response.json()
    print(f"  Cycles: {cycles['count']}")
    
    print("\n✅ Graph features ready to test!")
    print(f"\n🌐 Open: http://localhost:3000/policies/{POLICY_ID}/graph")
    print("\n🎯 Features to test:")
    print("  1. Click 'Highlight Conflicts' - should highlight Rule 2 and Rule 3 in red")
    print("  2. Click on any node - should show details panel")
    print("  3. Click 'Export PNG' - should download image")
    print("  4. Click 'Toggle Layout' - should rearrange graph")
    print("  5. Check conflict list below graph - should show 1 conflict")

if __name__ == "__main__":
    main()
