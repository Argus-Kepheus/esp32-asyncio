# Automated host-side tests

This directory contains the repository's **automated software tests**. They run
under CPython and are deliberately separate from the manual Wokwi/physical
hardware diagnostics in [`diagnostics/`](../diagnostics/).

## Run

```text
python -m unittest discover -s tests -p "test_*.py" -v
```

The ordered suite metadata is in [`metadata.json`](metadata.json).

## Current coverage

- `test_config_generation.py` — verifies deterministic
  `config/*.json → lib/generated_config.py` generation, unique generated
  names and coherent blink-speed policy.
- `test_documentation_contract.py` — verifies EN/PT/ES document IDs,
  revisions, semantic sections and exact generated documentation regions.
- `test_source_contracts.py` — parses `main.py` with CPython's AST and
  verifies the generated-config import boundary, root driver imports, async
  entry point and absence of blocking `time.sleep*` calls.

## Boundary

A passing host-side test suite does **not** prove:

- MicroPython peripheral API compatibility;
- successful Wokwi execution;
- real-hardware electrical behavior;
- scheduler jitter, bus latency or debounce behavior under physical load.

Those remain the responsibility of manual diagnostics or a future simulator /
hardware automation layer.
