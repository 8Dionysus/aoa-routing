# Spark Swarm Recipe — aoa-routing

Рекомендуемый путь назначения: `Spark/SWARM.md`

## Для чего этот рой
Используй Spark здесь для тонкого детерминированного роутинга: schema checks, registry/hints parity, inspect/expand target integrity, generated surface parity и тестов вокруг builder/validator. Рой не должен тащить сюда новые meaning layers.

## Читать перед стартом
- `README.md`
- `scripts/build_router.py`
- `scripts/validate_router.py`
- `schemas/`
- `tests/`

## Форма роя
- **Coordinator**: выбирает один invariant: registry parity, inspect/expand integrity, schema contract или fixture edge case
- **Scout**: картографирует source catalogs, generated outputs, tests и риск drift
- **Builder**: правит код/schema/tests минимальным diff
- **Verifier**: строит роутер, валидирует outputs и запускает тесты
- **Boundary Keeper**: не даёт рою вылезти за thin-router contract

## Параллельные дорожки
- Lane A: builder / validator / schema fix
- Lane B: tests / fixtures / edge cases
- Lane C: generated output refresh only if needed
- Не запускай больше одного пишущего агента на одну и ту же семью файлов.

## Allowed
- чинить `cross_repo_registry.min.json` / `aoa_router.min.json` parity surfaces
- усиливать tests для inspect/expand targets
- добавлять schema coverage и fixture coverage
- чинить source-catalog assumptions, не трогая upstream meaning

## Forbidden
- добавлять pairings
- добавлять same-kind relation graphs
- добавлять memo recall surfaces
- расширять слой до broader KAG/graph views
- парсить live source markdown как новый источник смысла

## Launch packet для координатора
```text
We are working in aoa-routing with a one-repo one-swarm setup.
Pick exactly one invariant:
- registry parity
- inspect/expand target integrity
- schema coverage
- fixture edge case
- generated output rebuild parity

First return:
1. the invariant
2. exact files to touch
3. whether generated outputs are expected to change
4. which lane each agent owns

The swarm must preserve the thin-router contract:
source repos own meaning; routing owns navigation.
```

## Промпт для Scout
```text
Map only. Do not edit.
Return:
- which generated files and tests cover the chosen invariant
- which sibling source catalogs are consumed
- likely failure points
- whether a rebuild is required or a pure test/schema change is enough
```

## Промпт для Builder
```text
Make the smallest reviewable change.
Rules:
- preserve deterministic thin-router behavior
- do not add new semantic layers
- if generated outputs change, note exactly why
- keep the diff bounded to the chosen invariant
```

## Промпт для Verifier
```text
Run the repo validation loop and report actual results.
Required:
- python -m pip install -r requirements-dev.txt
- python scripts/build_router.py
- python scripts/validate_router.py
- pytest
Return:
- commands run
- whether generated outputs changed
- any remaining integrity gaps
```

## Промпт для Boundary Keeper
```text
Review only for anti-scope.
Check:
- no pairings
- no same-kind graphs
- no memo recall surfaces
- no broader KAG views
- no upstream meaning copied into routing
- generated files changed only when justified
```

## Verify
```bash
python -m pip install -r requirements-dev.txt
python scripts/build_router.py
python scripts/validate_router.py
pytest
```

## Done when
- один invariant tightened
- тонкий роутер остался thin and deterministic
- generated outputs и tests согласованы
- anti-scope пройден без нарушений

## Handoff
Если обнаружен drift upstream catalog surfaces, follow-up почти всегда идёт в `aoa-techniques`, `aoa-skills` или `aoa-evals`, а не сюда.
