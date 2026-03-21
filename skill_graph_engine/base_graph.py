import networkx as nx


# Edge format: (prerequisite, skill)
_BASE_EDGES = [
    # Programming Foundations
    ("Programming Basics", "Data Structures"),
    ("Programming Basics", "Algorithms"),
    ("Data Structures", "Algorithms"),

    # Web Development
    ("Programming Basics", "HTML/CSS"),
    ("HTML/CSS", "JavaScript"),
    ("JavaScript", "React"),
    ("JavaScript", "Node.js"),
    ("Node.js", "REST API Design"),
    ("React", "TypeScript"),
    ("JavaScript", "TypeScript"),

    # Backend & Databases
    ("Programming Basics", "SQL"),
    ("SQL", "PostgreSQL"),
    ("REST API Design", "System Design"),
    ("PostgreSQL", "System Design"),

    # DevOps & Cloud
    ("Programming Basics", "Git"),
    ("Git", "CI/CD"),
    ("System Design", "AWS"),
    ("CI/CD", "AWS"),
    ("AWS", "Docker"),
    ("Docker", "Kubernetes"),

    # Data & ML
    ("Programming Basics", "Python"),
    ("Python", "Statistics"),
    ("Python", "NumPy"),
    ("Statistics", "Machine Learning"),
    ("NumPy", "Machine Learning"),
    ("Machine Learning", "Deep Learning"),
    ("Machine Learning", "NLP"),
    ("Deep Learning", "NLP"),

    # Soft Skills
    ("Communication", "Leadership"),
    ("Leadership", "Agile/Scrum"),
]

# Node default importance weights
_NODE_IMPORTANCE = {
    "Programming Basics": 0.9,
    "Data Structures": 0.85,
    "Algorithms": 0.85,
    "HTML/CSS": 0.6,
    "JavaScript": 0.85,
    "TypeScript": 0.8,
    "React": 0.85,
    "Node.js": 0.8,
    "REST API Design": 0.8,
    "SQL": 0.8,
    "PostgreSQL": 0.75,
    "System Design": 0.9,
    "Git": 0.75,
    "CI/CD": 0.75,
    "AWS": 0.8,
    "Docker": 0.75,
    "Kubernetes": 0.7,
    "Python": 0.85,
    "Statistics": 0.75,
    "NumPy": 0.65,
    "Machine Learning": 0.85,
    "Deep Learning": 0.8,
    "NLP": 0.75,
    "Communication": 0.7,
    "Leadership": 0.65,
    "Agile/Scrum": 0.65,
}


def build_base_graph() -> nx.DiGraph:
    G = nx.DiGraph()

    for node, importance in _NODE_IMPORTANCE.items():
        G.add_node(node, importance=importance, proficiency=0.0, confidence=0.0)

    G.add_edges_from(_BASE_EDGES)

    return G
