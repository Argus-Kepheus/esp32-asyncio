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

Since Wave 6, `main.py` imports this module directly through
`lib.generated_config`. Pin assignments, bus IDs/frequencies, application
runtime timings, blink-speed policy and console colors therefore no longer
have competing inline definitions in `main.py`.

`lib/__init__.py` makes this directory an explicit MicroPython package. The
display drivers remain at repository root during Wave 6 to preserve the
established Wokwi/mpremote workflow and avoid moving code without a concrete
maintenance benefit.
