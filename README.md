# IRAM Agent Team

An autonomous, testable multi-agent engineering framework uniting **OpenRig-style YAML roles**, **LangGraph cyclic state machines**, **Model Context Protocol (MCP)** tool execution, **ToolGate deterministic security filtering**, and **Opik/DeepEval observability**.

---

## 🏛️ Architecture

```
User Task ──► Architect ──► Developer ──► ToolGate Firewall ──► Local/MCP Tool
                               ▲              │
                               │              ▼
                           QA Tester ◄──── Execution
                               │
                        (Tests Pass?)
                          ├── No  ──► Feedback Loop to Developer
                          └── Yes ──► Security Reviewer ──► Approved
```

## 🚀 Usage

Run the team CLI on any engineering task:

```bash
iram-team "Implement user authentication with JWT" --test-cmd "pytest tests/ -q"
```

### CLI Options:
* `task` (positional): The software engineering goal or feature description.
* `--test-cmd`: Command executed by the QA agent to verify tests (default: `pytest tests/ -q`).
* `--max-iterations`: Maximum cyclic self-healing iterations before escalation (default: `5`).
* `--config`: Path to standing team specification (default: `config/team.yaml`).

## 🧪 Running Unit Tests

```bash
python3 -m unittest discover tests -v
```
