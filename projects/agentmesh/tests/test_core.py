import pytest

from agentmesh import Agent, AllowAllPolicy, DenyAllPolicy, Memory, StaticPlanner, Tool, ToolPolicy


def add(a, b):
    return a + b


def test_tool_execution_and_events():
    agent = Agent([Tool("add", add)], policy=AllowAllPolicy())
    result = agent.run([{"tool": "add", "args": {"a": 2, "b": 3}}])
    assert result.output == [5]
    assert [e.type for e in result.events][-1] == "run.completed"


def test_deny_by_default():
    agent = Agent([Tool("add", add)])
    with pytest.raises(PermissionError):
        agent.run([{"tool": "add", "args": {"a": 1, "b": 2}}])


def test_allowlist_policy():
    agent = Agent([Tool("add", add)], policy=ToolPolicy({"add"}))
    assert agent.run([{"tool": "add", "args": {"a": 4, "b": 6}}]).output == [10]


def test_dry_run_does_not_call_tool():
    calls = []
    agent = Agent([Tool("side_effect", lambda: calls.append(1))], policy=AllowAllPolicy())
    agent.run([{"tool": "side_effect"}], dry_run=True)
    assert calls == []


def test_planner_and_memory():
    memory = Memory(limit=2)
    agent = Agent([Tool("add", add)], policy=AllowAllPolicy(), planner=StaticPlanner([
        {"tool": "add", "args": {"a": 1, "b": 1}},
    ]), memory=memory)
    assert agent.run(goal="calculate").output == [2]
    assert memory.snapshot()[0]["result"] == 2


def test_step_limit():
    agent = Agent([Tool("add", add)], policy=AllowAllPolicy(), max_steps=1)
    with pytest.raises(RuntimeError):
        agent.run([{"tool": "add", "args": {"a": 1, "b": 1}}, {"tool": "add", "args": {"a": 2, "b": 2}}])


def test_retry_then_success():
    attempts = {"n": 0}

    def flaky():
        attempts["n"] += 1
        if attempts["n"] == 1:
            raise ValueError("temporary")
        return "ok"

    agent = Agent([Tool("flaky", flaky)], policy=AllowAllPolicy(), retries=1)
    assert agent.run([{"tool": "flaky"}]).output == ["ok"]
    assert attempts["n"] == 2
