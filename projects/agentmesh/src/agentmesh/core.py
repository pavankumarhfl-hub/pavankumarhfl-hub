from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic
from typing import Any, Callable, Protocol


class Planner(Protocol):
    def plan(self, goal: str) -> list[dict[str, Any]]: ...


@dataclass(frozen=True)
class Tool:
    name: str
    handler: Callable[..., Any]
    description: str = ""


@dataclass(frozen=True)
class Action:
    tool: str
    args: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Event:
    type: str
    data: dict[str, Any]


@dataclass(frozen=True)
class RunResult:
    output: list[Any]
    events: list[Event]


class Policy:
    def allow(self, action: Action) -> bool:
        raise NotImplementedError


class AllowAllPolicy(Policy):
    def allow(self, action: Action) -> bool:
        return True


class DenyAllPolicy(Policy):
    def allow(self, action: Action) -> bool:
        return False


class ToolPolicy(Policy):
    def __init__(self, allowed_tools: set[str]):
        self.allowed_tools = frozenset(allowed_tools)

    def allow(self, action: Action) -> bool:
        return action.tool in self.allowed_tools


class ToolRegistry:
    def __init__(self, tools: list[Tool] | None = None):
        self._tools: dict[str, Tool] = {}
        for tool in tools or []:
            self.register(tool)

    def register(self, tool: Tool) -> None:
        if not tool.name or not tool.name.strip():
            raise ValueError("tool name must not be empty")
        if tool.name in self._tools:
            raise ValueError(f"duplicate tool: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"unknown tool: {name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))


class Memory:
    def __init__(self, limit: int = 100):
        if limit < 1:
            raise ValueError("memory limit must be >= 1")
        self.limit = limit
        self.items: list[Any] = []

    def add(self, item: Any) -> None:
        self.items.append(item)
        if len(self.items) > self.limit:
            del self.items[:-self.limit]

    def snapshot(self) -> list[Any]:
        return list(self.items)


class StaticPlanner:
    """Planner useful for deterministic tests and applications without an LLM."""

    def __init__(self, actions: list[dict[str, Any]]):
        self.actions = list(actions)

    def plan(self, goal: str) -> list[dict[str, Any]]:
        return list(self.actions)


class Agent:
    def __init__(
        self,
        tools: list[Tool] | None = None,
        policy: Policy | None = None,
        planner: Planner | None = None,
        memory: Memory | None = None,
        max_steps: int = 20,
        timeout_seconds: float = 30.0,
        retries: int = 0,
    ):
        if max_steps < 1:
            raise ValueError("max_steps must be >= 1")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be > 0")
        if retries < 0:
            raise ValueError("retries must be >= 0")
        self.tools = ToolRegistry(tools)
        self.policy = policy or DenyAllPolicy()
        self.planner = planner
        self.memory = memory or Memory()
        self.max_steps = max_steps
        self.timeout_seconds = timeout_seconds
        self.retries = retries

    def run(self, actions: list[dict[str, Any]] | None = None, *, goal: str | None = None, dry_run: bool = False) -> RunResult:
        if actions is None:
            if self.planner is None or goal is None:
                raise ValueError("provide actions or both planner and goal")
            actions = self.planner.plan(goal)

        events: list[Event] = []
        output: list[Any] = []
        started = monotonic()
        events.append(Event("run.started", {"goal": goal, "dry_run": dry_run}))

        if len(actions) > self.max_steps:
            raise RuntimeError("maximum step limit exceeded")

        for index, raw in enumerate(actions, start=1):
            action = Action(tool=str(raw.get("tool", "")), args=dict(raw.get("args", {})))
            events.append(Event("action.proposed", {"step": index, "tool": action.tool}))
            if monotonic() - started > self.timeout_seconds:
                events.append(Event("run.timeout", {"step": index}))
                raise TimeoutError("agent run exceeded timeout budget")
            if not self.policy.allow(action):
                events.append(Event("action.denied", {"step": index, "tool": action.tool}))
                raise PermissionError(f"tool denied by policy: {action.tool}")
            if dry_run:
                events.append(Event("action.skipped", {"step": index, "tool": action.tool}))
                continue

            tool = self.tools.get(action.tool)
            last_error: Exception | None = None
            for attempt in range(self.retries + 1):
                try:
                    value = tool.handler(**action.args)
                    output.append(value)
                    self.memory.add({"tool": action.tool, "result": value})
                    events.append(Event("action.completed", {"step": index, "tool": action.tool, "attempt": attempt + 1}))
                    last_error = None
                    break
                except Exception as exc:  # tool failures are isolated at the runtime boundary
                    last_error = exc
                    events.append(Event("action.failed", {"step": index, "tool": action.tool, "attempt": attempt + 1, "error": type(exc).__name__}))
            if last_error is not None:
                raise last_error

        events.append(Event("run.completed", {"steps": len(actions), "outputs": len(output)}))
        return RunResult(output=output, events=events)
