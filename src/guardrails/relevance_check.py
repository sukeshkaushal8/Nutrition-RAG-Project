"""
Relevance check module — evaluates if retrieved chunks meet the distance threshold.

Implemented in Phase 5.
"""

def min_distance(results: list[dict]) -> float:
    """
    Returns the minimum distance (highest relevance) among retrieved chunks.
    If no chunks were retrieved, returns a very high distance (e.g. 1.0)
    so it fails the threshold check.
    """
    if not results:
        return 1.0
        
    return min(res.get("distance", 1.0) for res in results)
