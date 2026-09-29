"""
Scope Guard module — checks if a query falls into blocked topics like medical advice.

Implemented in Phase 5.
"""

import re

BLOCKED_TOPICS = [
    "medical advice", "diagnos", "prescri", "medication",
    "calorie target", "calorie goal", "weight loss", "lose weight",
    "bmi", "body mass index", "how much should i weigh", "should i weigh",
    "diet plan for weight", "eating disorder", "supplement"
]

def is_out_of_scope(query: str) -> bool:
    """
    Check if the query contains any of the blocked topics.
    Returns True if the query is out of scope.
    """
    query_lower = query.lower()
    for topic in BLOCKED_TOPICS:
        if topic in query_lower:
            return True
    return False
