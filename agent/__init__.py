# Agent module initialization
# Hybrid architecture: Deterministic conversation + Agentic processing

from agent.state import ClaimState, create_initial_state, AgentTrace, ToolInvocation, ReasoningStep
from agent.workflow_agent import graph, get_reasoning_trace, get_processing_summary

# For backwards compatibility, also expose tools
from agent.tools_agent import PROCESSING_TOOLS, TOOL_MAP

__all__ = [
    "ClaimState",
    "create_initial_state",
    "AgentTrace",
    "ToolInvocation",
    "ReasoningStep",
    "graph",
    "get_reasoning_trace",
    "get_processing_summary",
    "PROCESSING_TOOLS",
    "TOOL_MAP"
]
