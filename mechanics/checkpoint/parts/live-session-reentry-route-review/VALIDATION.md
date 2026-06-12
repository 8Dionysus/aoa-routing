# Validation

Run the part test:

`python -m pytest -q mechanics/checkpoint/parts/live-session-reentry-route-review/tests`

Run the repo-wide route validator:

`python scripts/validate_router.py`

The validator checks that the route review surface exists, validates against
its schema, names source-owned next actions, and keeps budget/checkpoint meaning
outside `aoa-routing`.
