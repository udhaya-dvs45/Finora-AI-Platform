"""
workflow package
----------------
Multi-Agent Orchestration Layer for Milestone 3.
Provides:
  - financial_workflow: LangGraph StateGraph pipeline
  - OrchestrationPipeline: Sequential agent pipeline
"""
from .orchestrator import OrchestrationPipeline
from .graph import financial_workflow, FinancialState

__all__ = ["OrchestrationPipeline", "financial_workflow", "FinancialState"]
