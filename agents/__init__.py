"""
agents/ — re-exports all agents from src/agents/
"""
import sys
import os

# Ensure src/agents is importable as 'agents.*'
SRC_AGENTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "agents")
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
