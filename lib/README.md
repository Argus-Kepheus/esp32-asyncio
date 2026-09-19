# Generated firmware support files

This directory is introduced by Wave 2.

## `generated_config.py`

This file is generated deterministically from:

- `config/hardware.json`
- `config/runtime.json`

Do not edit it manually.

Regenerate/check it with:

```text
python tools/generate_config.py --write
python tools/generate_config.py --check
```

The file is committed intentionally because MicroPython/Wokwi should receive a
plain Python module and should not need to parse the development-time JSON
configuration.

During Wave 2 the existing `main.py` still uses its historical inline
constants. The generated module is therefore a verified **derived artifact**,
not yet a runtime dependency. A later firmware wave may switch `main.py` to
import it after the configuration pipeline has already proven stable.
