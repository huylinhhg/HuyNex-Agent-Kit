# Contributing to HuyNex Agent Kit

We welcome contributions from developers worldwide!

---

## 🏛️ Development & Versioning Strategy

HuyNex Agent Kit distinguishes between **Core** and **Content**:

| Version Pattern | Scope of Change | Requires Core Mutation? | Risk Level |
| :--- | :--- | :---: | :---: |
| **Patch (v0.4.x)** | Bugfixes, adding new Skills (`.agents/skills/`), updating Rules | **No** (Frozen Core) | Low |
| **Minor (v0.5.0)** | Adding support for a new AI Agent adapter (e.g. Windsurf) | Conditional (Adapter only) | Medium |
| **Major (v1.0.0)** | Structural redesign of manifest schema or lifecycle engine | Yes (Requires migration tests) | High |

---

## 🛠️ Development & Quality Gates

Before submitting any Pull Request or pushing changes:

1. **Verify Secret & Skill Formatting**:
   ```bash
   python3 scripts/validate.py
   ```
2. **Run Full Regression Suite (Must PASS 100%)**:
   ```bash
   python3 -m unittest discover -s tests -p "test_*.py" -v
   ```
3. **Run Multi-Agent Lifecycle Smoke Test**:
   ```bash
   python3 scripts/ci_multi_agent_smoke.py
   ```
4. **Run Distillation Benchmark**:
   ```bash
   python3 bin/huynex-distill --benchmark
   ```

---

## 🛡️ Coding & Safety Standards

- **Core Immutability**: Do NOT modify `scripts/install.py` when only adding new skills or modifying rules.
- **Fail-Closed Verification**: Never allow gates or tests to pass on missing evidence.
- **Data Safety Contract**: All contributions must strictly conform to [docs/DATA_SAFETY_CONTRACT.md](docs/DATA_SAFETY_CONTRACT.md).
- **Pure Standard Library**: Keep the core kit running on standard library Python without requiring extra pip packages.
