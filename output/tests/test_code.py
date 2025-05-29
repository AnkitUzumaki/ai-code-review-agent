"""Module docstring"""
import pytest
from input.test import greet

def test_greet():
    """Docstring for test_greet"""
    assert greet('World') is None
