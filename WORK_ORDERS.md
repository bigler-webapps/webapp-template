# Work-Order Register - WORK_ORDERS.md — webapp-template

## Workstream prefixes

| Prefix | Workstream |
|---|---|
| `TPL-*` | Preventive template baseline work inherited by newly scaffolded applications |
| `WT-DEP-*` | Dependency declarations of the template: what every new app pins and installs |

Introduce a new prefix when none fits and add it here. New WOs always get a
prefixed ID; never reuse a bare flat number across workstreams.

The register is `work-orders/register.jsonl` (one JSON object per work order); read and write it only
through `python -I .claude/scripts/wo.py` (`AGENTS.md` -> "Work-Order Register"). Completion details
live in the "Completion" section of each `work-orders/<ID>.md`. The register as it stood before the
migration is archived whole in `work-orders/archive/WORK_ORDERS-until-2026-11-16.md`.

**Repo token:** see the declaration above
