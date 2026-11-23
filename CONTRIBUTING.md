# Contributing to HuyNex Agent Kit

We welcome contributions from developers worldwide!

---

## 🛠️ Development Workflow

1. Fork and clone the repository.
2. Ensure you have Python 3.10+ installed.
3. Run the validation suite:
   ```bash
   python3 scripts/validate.py
   ```
4. Run all unit tests:
   ```bash
   python3 -m unittest discover -s tests -p "test_*.py" -v
   ```
5. Ensure code formatting is clean, minimal, and adheres to the **Ladder of Laziness** (avoid unnecessary abstractions or external dependencies).

---

## 🛡️ Coding & Safety Standards

- **Zero Hardcoded Personal Paths**: Always use dynamic paths or variables (`$HOME`, `$PWD`).
- **Fail-Closed Verification**: Never allow gates or tests to pass on missing evidence.
- **Pure Standard Library**: Keep the core kit running on standard library Python without requiring extra pip packages.
