import sys
def generate_graphviz_from_bullet_points(lines):
    """
    Transform bullet point format to Graphviz DOT format
    
    Expected input format:
    - Main entity
      - Direction 1
        - Subsidiary 1
          - Sub-sub 1
          - Sub-sub 2
        - Subsidiary 2
      - Direction 2
    - Rank 1 Subsidiary 1
      - Sub-sub 3
    - Rank 1 Subsidiary 2
    """
    # Parse hierarchy
    entities = []
    for line in lines:
        if line.strip():
            indent_level = (len(line) - len(line.lstrip())) // 2
            name = line.strip().lstrip('- ')
            entities.append((indent_level, name))
    
    # Group by levels
    level_entities = {}
    entity_parents = {}
    
    # Find parent-child relationships
    stack = []
    for indent, name in entities:
        # Adjust stack to current level
        while len(stack) > indent:
            stack.pop()
            
        if stack:
            entity_parents[name] = stack[-1]
        
        if indent not in level_entities:
            level_entities[indent] = []
        if name not in level_entities[indent]:
            level_entities[indent].append(name)
            
        stack.append(name)
    
    # Generate DOT output
    dot_lines = ["digraph G {"]
    dot_lines.append('    rankdir=TB;')
    dot_lines.append('    node [shape=none];')
    dot_lines.append("")

    # Add nodes by level with appropriate styling
    max_level = max(level_entities.keys()) if level_entities else 0
    
    for level in range(max_level + 1):
        if level in level_entities:
            # Define visual attributes based on your specific requirements:
            # - Level 0: Root items (EDF SA = lightblue, others = lightyellow)
            # - Level 1: Direct children of EDF SA (directions = lightblue) 
            # - Others: lightgray
            if level == 0:
                dot_lines.append("    // Root level entities")
                for entity in level_entities[level]:
                    if entity == "EDF SA":
                        add_root(dot_lines, entity)
                    else:
                        # Other root level items are rank 1 subsidiaries
                        add_rank1_subsidiary(dot_lines, entity)
                        entity_parents[entity] = "EDF SA"
            elif level == 1:
                dot_lines.append("    // Level 1 (Directions and direct children of EDF SA)")
                for entity in level_entities[level]:
                    # Check if parent is EDF SA
                    if entity_parents.get(entity) == "EDF SA":
                        # Directions under EDF SA are lightblue
                        add_direction(dot_lines, entity)
                    else:
                        # Other level 1 items are lightgray
                        add_sub_subsidiary(dot_lines, entity)
            else:
                # Level 2 and deeper are all lightgray (sub subsidiaries)
                dot_lines.append(f"    // Level {level} (Sub subsidiaries)")
                for entity in level_entities[level]:
                    add_sub_subsidiary(dot_lines, entity)
            dot_lines.append("")

    # Add actual relationships
    dot_lines.append("    // Relationships")
    for child, parent in entity_parents.items():
        if parent == "EDF SA":
            dot_lines.append(f'    "{clean(parent)}" -> "{clean(child)}" [style=invis];')
        else:
            dot_lines.append(f'    "{clean(parent)}" -> "{clean(child)}";')
    
    dot_lines.append("}")
    
    return "\n".join(dot_lines)


def clean(entity):
    if entity.startswith("D1:") or entity.startswith("R1:"):
      return entity[3:].strip()
    return entity


def add_sub_subsidiary(dot_lines, entity):
    if entity.startswith("D1:"):
      dot_lines.append(f'    "{clean(entity)}" [cluster=1 clustercolor=lightblue];')
    elif entity.startswith("R1:"):
      dot_lines.append(f'    "{clean(entity)}" [cluster=2 clustercolor=lightyellow];')
    else:
      dot_lines.append(f'    "{clean(entity)}" [cluster=3 clustercolor=lightgray];')


def add_direction(dot_lines, entity):
    dot_lines.append(f'    "{clean(entity)}" [cluster=1 clustercolor=lightblue];')


def add_rank1_subsidiary(dot_lines, entity):
    dot_lines.append(f'    "{clean(entity)}" [cluster=2 clustercolor=lightyellow];')


def add_root(dot_lines, entity):
    dot_lines.append(f'    "{clean(entity)}" [cluster=1 clustercolor=lightblue];')


# Example usage
bullet_points = """
- Main entity
  - Direction 1
    - Subsidiary 1
      - Sub-sub 1
      - Sub-sub 2
    - Subsidiary 2
  - Direction 2
- Rank 1 Subsidiary 1
  - Sub-sub 3
- Rank 1 Subsidiary 2
"""
lines = bullet_points.strip().split('\n')
dot_output = generate_graphviz_from_bullet_points(sys.stdin.readlines())
print(dot_output)
