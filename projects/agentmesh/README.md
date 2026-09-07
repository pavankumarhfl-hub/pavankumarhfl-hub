# AgentMesh

**Open-source agent runtime for building tool-using AI systems with explicit planning, memory, permissions, and auditable execution.**

AgentMesh is the fourth project in the public engineering portfolio of **Pavan Kumar BN**. It is designed to bridge AI agents with the engineering discipline demonstrated by RepoLens, SecretSentry, and JobForge.

## Why AgentMesh?

A useful agent needs more than a chat loop. It needs a controlled execution model:

```text
Goal
  ↓
Planner → Tool Registry → Policy Gate → Executor
  ↑                              ↓
Memory ← Observation ← Result ← Tool
```

The runtime separates **what an agent wants to do** from **what it is allowed to do** and records each step as an auditable event.

## v0.1 capabilities

- Model-agnostic planner interface
- Typed tool registry
- Explicit tool permissions
- Deterministic policy gate
- Short-term working memory
- Structured execution events
- Step limits and timeout budget
- Retry handling for transient tool failures
- Dry-run mode
- JSON event export
- Zero runtime dependencies

## Quick start

```python
from agentmesh import Agent, Tool, AllowAllPolicy

agent = Agent(
    tools=[Tool("add", lambda a, b: a + b)],
    policy=AllowAllPolicy(),
)

result = agent.run([{"tool": "add", "args": {"a": 2, "b": 3}}])
print(result.output)
```

## Architecture

AgentMesh deliberately keeps the runtime small and composable:

- **Planner** produces structured actions. A real LLM adapter can implement this interface without changing the runtime.
- **Tool Registry** validates tool names and arguments before execution.
- **Policy** decides whether an action is permitted.
- **Executor** applies limits, retries, and dry-run behavior.
- **Memory** stores bounded working context.
- **Events** provide an audit trail for every decision and result.

## Security model

AgentMesh is designed around least privilege. Tools should be registered explicitly, policies should deny unsafe capabilities by default, and applications should never give an agent unrestricted filesystem, shell, network, or credential access without an intentional policy.

This project does **not** provide autonomous access to user accounts or systems. Integrations are application-controlled.

## Open-source direction

Planned extensions:

1. Provider adapters for major LLM APIs
2. Persistent memory backends
3. Human approval checkpoints
4. Tool schemas and JSON Schema validation
5. Streaming events
6. Parallel task execution
7. Agent-to-agent protocols
8. Evaluation and replay tooling
9. OpenTelemetry integration
10. Web dashboard for traces and policy decisions

## Engineering goals

AgentMesh aims to be:

- **Composable** — small interfaces instead of a monolithic framework.
- **Auditable** — every action can produce structured events.
- **Secure by design** — policy is a first-class runtime boundary.
- **Provider-neutral** — model integrations live outside the core.
- **Testable** — planners, policies, tools, and executors are independently testable.
- **Fast to adopt** — standard library only for the core.

## Development

```bash
python -m pytest -q
```

## License

MIT © Pavan Kumar BN
