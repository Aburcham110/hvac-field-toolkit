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
hvac-sh-sc -r R-410A --suction-psig 118 --suction-temp 40 --liquid-psig 200 --liquid-temp 50

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
