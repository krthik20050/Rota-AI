---
title: Contributing Guidelines
---

We welcome contributions to Rota AI! To maintain code quality, security, and stability, please adhere to these guidelines.

---

### Code Quality Standards
- **Linter**: We use `ruff` to enforce PEP 8 styles and import sorting. Run `ruff check .` inside `/desktop` before committing.
- **Typing**: Use standard Python type hinting (`typing` module) for all function arguments and return signatures.
- **Error Handling**: Never swallow exceptions with naked `except:` statements. Log errors using our structured logging system:
  ```python
  from utils.log import get_logger
  logger = get_logger(__name__)

  try:
      # Code...
  except Exception as e:
      logger.exception("Descriptive error message", extra={"correlation_id": "xyz"})
  ```

---

### Testing Protocol
Before submitting a Pull Request, run the unit test suite to verify no regressions occurred:
```bash
# From Rota-AI/desktop
pytest tests/
```

If you add a new service or platform hook, you are required to write matching tests under `/desktop/tests/`.

---

### Pull Request Lifecycle
1. **Fork** the repository and create a new feature branch (e.g., `feature/improved-linux-hotkey`).
2. Implement your changes. Write comprehensive comments detailing *what* the change does and *why* it was designed that way.
3. Verify formatting using `ruff format .`.
4. Ensure all tests pass.
5. Push to your fork and open a **Pull Request**. The CI actions will test your code across Windows and Linux environments.
