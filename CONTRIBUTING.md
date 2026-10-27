# Contributing

Bug reports, fixes and new ideas are welcome.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

## Guidelines

- Keep each pull request focused on one change.
- Add or update a test in `tests/` for any change in behaviour.
- Make sure `pytest` passes before you open the pull request.
- When changing the physics, explain the derivation in the pull request and update `docs/theory.md` if the equations change.
