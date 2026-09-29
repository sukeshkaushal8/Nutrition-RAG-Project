import pytest
from src.guardrails.scope_guard import is_out_of_scope
from src.guardrails.relevance_check import min_distance

def test_scope_guard_out_of_scope():
    assert is_out_of_scope("Should I take vitamin D supplements?") is True
    assert is_out_of_scope("What should I weigh for my height?") is True
    assert is_out_of_scope("Give me a diet plan for weight loss") is True
    assert is_out_of_scope("What is my ideal BMI?") is True
    assert is_out_of_scope("How to diagnos my headache?") is True

def test_scope_guard_in_scope():
    assert is_out_of_scope("How long can I keep chicken in the fridge?") is False
    assert is_out_of_scope("What does WHO recommend for salt intake?") is False
    assert is_out_of_scope("Are saturated fats bad for you?") is False

def test_relevance_check_valid_distance():
    results = [
        {"distance": 0.50},
        {"distance": 0.21},
        {"distance": 0.35}
    ]
    assert min_distance(results) == 0.21

def test_relevance_check_empty_results():
    assert min_distance([]) == 1.0

def test_relevance_check_all_high_distance():
    results = [
        {"distance": 0.60},
        {"distance": 0.75}
    ]
    assert min_distance(results) == 0.60
