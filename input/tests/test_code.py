# input/tests/test_code.py
import pytest
from input.test import greet

def test_greet():
    assert greet("World") is None  # Print-based function
