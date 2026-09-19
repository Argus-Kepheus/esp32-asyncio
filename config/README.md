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

## Transitional state after Wave 1

Existing values in `main.py`, `diagram.json`, `docs/`, and `tests/`
still repeat some of the same facts. They are retained intentionally in Wave 1
to avoid combining governance changes with behavioral or structural changes.

Starting with Wave 2:

1. generated firmware configuration can be derived from these canonical files;
2. validators can compare `diagram.json` and derived artifacts against them;
3. documentation tables can later be generated or validated from the same
   data;
4. stale manual copies can progressively be replaced by references or generated
   content.

Until Wave 2 validation exists, changes to hardware or runtime policy should be
made in `config/` first and then mirrored carefully to the current executable
and documentation so that the repository remains operational.

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
