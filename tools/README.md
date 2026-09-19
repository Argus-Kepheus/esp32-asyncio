# Repository tooling

Development-time utilities for keeping the repository synchronized with the
canonical configuration introduced in Waves 1 and 2.

These scripts run on the development machine with CPython. They are **not**
copied to or executed by the ESP32.

## Generate MicroPython configuration

```text
python tools/generate_config.py --check
python tools/generate_config.py --write
```

The generator reads:

- `config/hardware.json`
- `config/runtime.json`

and deterministically produces:

- `lib/generated_config.py`

The generated module is committed intentionally so the MicroPython/Wokwi
project does not need a JSON parser or a pre-build step at runtime.

## Validate repository consistency

```text
python tools/validate_repository.py
```

The Wave 2 validator checks:

- internal consistency of canonical GPIO assignments;
- unsafe use of ESP32 input-only pins as outputs;
- exact generated configuration consumed by `main.py`;
- absence of canonical configuration redefinitions inside `main.py`;
- use of generated I2C/SPI bus IDs, TFT baudrate and blink-speed policy;
- component IDs and Wokwi part types in `diagram.json`;
- LED colors and resistor values;
- OLED I2C addresses;
- key bindings for buttons;
- electrical connectivity of LEDs, buttons, pull-down resistors, displays,
  and the flash-mode switch;
- exact reproducibility of `lib/generated_config.py`;
- multilingual documentation parity from `docs/metadata.json`;
- document IDs, languages, shared content revisions, and required semantic sections;
- reappearance of known stale documentation statements found during Wave 0/3.

## Boundary of the validator

A successful static validation means the repository representations agree with
the canonical configuration. It does **not** prove:

- MicroPython runtime compatibility;
- correct Wokwi simulation behavior;
- real-hardware electrical behavior;
- timing guarantees under load;
- physical debounce performance.

Those remain separate simulation/hardware validation activities.

## Documentation parity

Wave 3 adds a semantic parity contract for EN/PT/ES documentation.

The validator reads `docs/metadata.json` and verifies that each maintained
language:

- contains every registered document;
- uses the correct stable document ID;
- declares the same content revision as the canonical EN document;
- implements all required language-neutral semantic section markers.

This is intentionally not a sentence-by-sentence translation comparison.
Translations may use natural language-specific structure and wording while
remaining normatively equivalent.

Spanish (ES) is now a maintained translation. Any additional language must be registered in `docs/metadata.json` and satisfy the same document/revision/section contract.


## Generate documentation blocks

```text
python tools/generate_docs.py --check
python tools/generate_docs.py --write
```

The documentation generator reads the canonical `config/hardware.json` and
`config/runtime.json` files and maintains the explicitly marked generated
regions in EN/PT/ES documentation.

This allows several human-facing views of the same fact without creating
several independent sources of truth: the representations are duplicated for
usability, but their values are derived from one owner.

The repository validator also checks these regions byte-for-byte against the
generator output and rejects concrete wiring/passive-value duplication in the
component specification sheets.


## Manual diagnostics semantics

Wave 5 separated manual hardware diagnostics from automated tests; Wave 9 activates the automated layer:

- `diagnostics/` contains the 13 ordered Wokwi/physical-hardware diagnostic
  scripts and `diagnostics/metadata.json`;
- `tests/` contains the Wave 9 host-side automated `unittest` suite;
- a manual diagnostic requires an observed simulator/physical result and is
  not automatically equivalent to a passing software test.

The repository validator checks the diagnostic inventory, ordering, docstring
identity, and stale references to the former manual-diagnostic paths.


## Firmware configuration boundary

Wave 6 makes `lib/generated_config.py` a runtime dependency of `main.py`.
The validator therefore checks that the generated names are imported and used,
and rejects reintroduction of competing inline definitions.

The display drivers remain at repository root in this wave. Moving them is not
required to establish a single configuration owner and would change the
existing Wokwi/mpremote deployment shape without a demonstrated benefit.


## Continuous integration

Wave 7 adds `.github/workflows/repository-validation.yml`.

On pushes to `main`, pull requests, and manual dispatch, GitHub Actions runs:

```text
python tools/generate_config.py --check
python tools/generate_docs.py --check
python tools/validate_repository.py
python -m unittest discover -s tests -p "test_*.py" -v
python -m py_compile ...
```

The workflow uses only CPython's standard library and does not modify the
repository. A failure means a generated artifact is stale, repository
representations disagree, documentation/diagnostic governance has regressed,
or Python syntax is invalid.

Passing CI is **not** evidence that the Wokwi simulation or physical ESP32 has
executed successfully. Manual diagnostics remain a separate validation layer.


## Host-side automated tests

Wave 9 activates the `tests/` namespace that Wave 5 reserved.

Run:

```text
python -m unittest discover -s tests -p "test_*.py" -v
```

The suite covers deterministic config generation, the EN/PT/ES documentation
contract and generated regions, plus static source invariants in `main.py`.
Its inventory and limitations are declared in `tests/metadata.json`.

These tests are intentionally host-side. They do not emulate MicroPython
peripheral APIs, Wokwi timing or physical ESP32 electrical behavior.
