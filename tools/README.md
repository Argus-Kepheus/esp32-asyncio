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
- canonical configuration versus the constants currently duplicated in
  `main.py`;
- I2C/SPI bus IDs and TFT SPI baudrate in `main.py`;
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

## Current transitional state

During Wave 2, `main.py` still defines its own constants and does not import
`lib/generated_config.py`. This is intentional: Wave 2 establishes the
generation/validation mechanism without changing firmware behavior.

A later firmware wave can switch `main.py` to consume the generated module
after the new configuration pipeline is already verifiable.


## Documentation parity

Wave 3 adds a semantic parity contract for EN/PT documentation.

The validator reads `docs/metadata.json` and verifies that each maintained
language:

- contains every registered document;
- uses the correct stable document ID;
- declares the same content revision as the canonical EN document;
- implements all required language-neutral semantic section markers.

This is intentionally not a sentence-by-sentence translation comparison.
Translations may use natural language-specific structure and wording while
remaining normatively equivalent.

A future language such as ES can be added by registering it in
`docs/metadata.json` and satisfying the same document/revision/section
contract.
