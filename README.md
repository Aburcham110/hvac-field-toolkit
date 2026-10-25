# HVAC Field Toolkit

Educational Python toolkit of field tools for HVAC/R technicians.

**Educational only** — verify with OEM literature, a calibrated instrument, and your Authority Having Jurisdiction (AHJ). Not a substitute for manufacturer selection software, a refrigerant-rated manifold, or proper lockout/tagout.

## Tools (v0.1)

| Command              | Purpose                                      |
|----------------------|----------------------------------------------|
| `hvac-sh-sc`         | Superheat & subcooling (R-410A, R-22, R-134a, R-404A, R-407C, R-32, R-454B) |
| `hvac-electrical`    | FLA/RLA amp compare, voltage imbalance       |
| `hvac-psych`         | Basic psychrometric approximations           |
| `hvac-airflow`       | Airflow / ΔT bands, rough CFM, ranked checks |
| `hvac-duct-static`   | Duct velocity, component ESP sum, static checklist |
| `hvac-charge`        | Approx line-set charge add/recover estimate  |
| `hvac-compressor`    | Compressor symptom tree → ranked checks + parts (LOTO reminders) |
| `hvac-txv-eev`       | TXV / EEV ranked checks tied to SH/SC        |
| `hvac-vacuum`        | Evacuation coach, micron hold/decay interpretation, pre-charge list |
| `hvac-leak-rate`     | Annualized leak-rate practice (NOT a compliance system) |
| `hvac-box-load`      | Walk-in cooler/freezer box-load estimate (not for bids) |
| `hvac-defrost`       | Cooler/freezer defrost & controls checklist  |
| `hvac-oil-rack`      | Commercial rack oil-system call tree         |
| `hvac-case-controller` | Case controller playbook (probes → wiring → controller) |
| `hvac-a2l`           | A2L (R-454B / R-32) field safety checklist   |
| `hvac-nameplate`     | Nameplate card + stub fault-code lookup      |
| `hvac-job-log`       | Job-log notes with 608-style fields (NOT compliance) |

More tools (TXV/EEV path, vacuum coach, box-load sizer, case controller playbook, A2L checklist, compressor diag, etc.) will be migrated from the individual repos.

## Install

```bash
# From a local clone
pip install -e .

# or for development (includes pytest)
pip install -e ".[dev]"
```

## Usage

```bash
# Superheat & subcooling
hvac-sh-sc -r R-410A --suction-psig 118 --suction-temp 52 --liquid-psig 318 --liquid-temp 90
# -> SH ~12 °F (dew), SC ~10 °F (bubble). Verify against the OEM PT chart.

# Electrical
hvac-electrical amps --measured 14.2 --fla 16.0 --rla 12.8
hvac-electrical imbalance --vab 240 --vbc 238 --vca 242

# Psychrometrics
hvac-psych --db 75 --rh 50

# Airflow / ΔT
hvac-airflow --system res-ac --supply 55 --return-temp 75

# Duct / static
hvac-duct-static --cfm 1200 --shape rect --width-in 20 --height-in 10 --filter-dp 0.25 --coil-dp 0.4

# Charge add/recover (approximate)
hvac-charge --system split-ac --refrigerant R-410A --factory-lbs 7.5 --liquid-ft 40 --liquid-od 3/8 --current-lbs 7.5

# Compressor diagnostics
hvac-compressor --symptom high-amps --sh 4

# TXV / EEV path
hvac-txv-eev --valve eev --symptom hunting --sh 3 --sc 10

# Vacuum / evacuation
hvac-vacuum --mode interpret-decay --start-micron 400 --after-micron 450 --minutes 10

# Leak-rate practice (educational only, not compliance)
hvac-leak-rate --full-charge-lbs 100 --added-lbs 10 --days 182.5 --category commercial-refrigeration

# Walk-in box load
hvac-box-load --length 8 --width 10 --height 8 --box-type cooler

# Defrost / controls checklist
hvac-defrost --box freezer --mode time-clock

# Rack oil call tree
hvac-oil-rack --symptom low-oil-alarm

# Case controller playbook
hvac-case-controller --focus probes

# A2L field checklist
hvac-a2l --refrigerant R-454B --job install

# Nameplate card + fault code lookup (stubbed database)
hvac-nameplate --brand Carrier --model 24ACC636 --code 33
hvac-nameplate --list-codes

# Job log (text or markdown)
hvac-job-log --technician "A. Tech" --customer "Acme" --refrigerant R-410A --format markdown
```

## Development

```bash
pytest
```

## Related

- Individual CLI repos (original educational tools)
- `service-tech-ui` — phone-friendly static UI / future PWA

## License

MIT
