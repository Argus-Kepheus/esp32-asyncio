# Canonical configuration

The `config/` directory is introduced by **Wave 1** of the repository
refactoring plan. Its purpose is to establish one authoritative owner for
technical facts that were previously repeated across firmware, Wokwi files,
diagnostics, and multilingual documentation.

Wave 1 does **not** change application behavior. `main.py`, `diagram.json`,
the diagnostics, and the existing documentation remain untouched during this
wave.

## Files

### `hardware.json`

Canonical owner for semantic hardware configuration:

- target board identity;
- component IDs and Wokwi part types;
- GPIO assignments and physical header references;
- I2C/SPI bus assignments;
- display addresses, dimensions, and driver association;
- resistor values;
- supply-rail assignments;
- button pull configuration;
- ESP32 pin constraints relevant to this project.

It is **not** the owner of Wokwi visual coordinates or wire-routing geometry.
Those remain in `diagram.json`.

### `runtime.json`

Canonical owner for application-level runtime policy:

- blinking-LED base interval;
- speed-control range;
- button sampling and debounce timing;
- CPU/RAM graph sampling cadence;
- serial status interval;
- console log throttling and RGB565 application colors.

Bus frequencies belong to `hardware.json`, because they configure hardware
interfaces rather than application scheduling.

## Authority model

A fact may appear in several places for usability, but only one file should
own it.

| Information | Canonical owner |
|---|---|
| Board/component identity | `config/hardware.json` |
| GPIO assignments | `config/hardware.json` |
| Bus assignments/frequencies | `config/hardware.json` |
| Electrical roles/resistors/supplies | `config/hardware.json` |
| Wokwi visual coordinates/wire routing | `diagram.json` |
| Local Wokwi simulator process/ports | `wokwi.toml` |
| Runtime timing/debounce/sampling | `config/runtime.json` |
| Functional requirements and rationale | canonical technical specification |
| Executable behavior | firmware |
| Academic report | `report/` snapshot; not an operational authority |

## Transitional state after Wave 2

Existing values in `main.py`, `diagram.json`, `docs/`, and the current
manual diagnostics still repeat some canonical facts. They remain in place
intentionally so configuration governance can be introduced before firmware or
folder structure is changed.

Wave 2 adds:

1. `tools/generate_config.py`, which deterministically derives
   `lib/generated_config.py` from these canonical files;
2. `tools/validate_repository.py`, which checks the canonical configuration
   against `main.py`, `diagram.json`, and the generated module;
3. static checks for GPIO conflicts, input-only pin misuse, component identity,
   resistor values, bus settings, display addresses, button key bindings, and
   electrical connectivity.

`main.py` does not import `lib/generated_config.py` yet. That integration is
deliberately deferred to the firmware-modularization wave so Wave 2 does not
change runtime behavior.

For changes to hardware or runtime policy, edit `config/` first, regenerate
with `python tools/generate_config.py --write`, and run
`python tools/validate_repository.py`. Until later documentation waves remove
manual duplication, affected documentation must still be reviewed separately.

## Provenance

The initial canonical configuration was extracted from repository state:

`2096a531e6386d44b52d936bbeb7589940cc2b17`

The primary evidence used was:

- `main.py`;
- `diagram.json`;
- `docs/EN/hardware-reference.md`;
- `docs/EN/component-specifications.md`.

Where historical documentation conflicted with the current circuit or firmware,
the current `main.py` + `diagram.json` state took precedence for the Wave 1
configuration. No historical documentation was corrected in this wave.


## Documentation after Wave 4

Human-readable documentation may show the same canonical fact in more than one
place, but high-risk repeated tables are now generated from `config/`.

`tools/generate_docs.py` currently derives hardware/runtime views in EN/PT.
Component sheets deliberately avoid duplicating concrete wiring/passive values,
and functional specifications reference generated hardware views instead of
maintaining separate pin maps.

This means duplication for usability is allowed only when it is **derived or
validated**, not independently authored.
