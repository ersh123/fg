import os
import sys

# Ensure src is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from skeleton import greet


def test_greet_default():
    assert greet() == "Hello, world!"


def test_greet_custom():
    assert greet("Codex") == "Hello, Codex!"
