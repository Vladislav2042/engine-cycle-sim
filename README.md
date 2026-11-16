# Engine Cycle Simulator

Thermodynamic cycle analysis of an air-breathing jet engine in Python: a complete turbojet/turbofan
cycle with cooled turbines, plus a **MIPCC** variant (mass injection pre-compressor cooling) that is
relevant to high-speed air-breathing propulsion.

The output is a temperature–entropy (T–s) diagram of the cycle, its enclosed area as a work proxy, and
both static and animated visualisations.

University coursework project, cleaned up for publication. Code comments are in Russian (original),
README in English.

## What is computed

A station-by-station cycle solve, `1 → 2 → 3 → 4 → 5 → 6 → 6' → 7 → 8`:

| Station | Component | Model |
|---|---|---|
| 1 → 2 | intake / diffuser | isentropic compression with total-pressure recovery `σ(М)`, subsonic `σ = 0.97` |
| 2 → 3 | low-pressure compressor | `π_LPC = 3.54`, `η = 0.85` |
| 3 → 4 | high-pressure compressor | `π_HPC = 6.46`, `η = 0.84` |
| 4 → 5 | combustion chamber | `T* = 1665 K`, `σ = 0.941`, `η = 0.98`, `H_u = 42.9 MJ/kg`, `L₀ = 14.8` |
| 5 → 6 | high-pressure turbine | `π_HPT = 2.9`, `η = 0.89`, 4 % cooling air bled from the HPC |
| 6 → 6' | cooling-air mixing | mass-weighted total temperature |
| 6' → 7 | low-pressure turbine | `π_LPT = 2.3`, `η = 0.91` |
| 7 → 8 | nozzle | velocity coefficient `φ = 0.98`, static exit temperature |

Entropy is integrated segment by segment with

```
Δs = cp·ln(T₂/T₁) − R·ln(P₂/P₁)
```

using separate `cp`, `R`, `k` for air and combustion products. The cycle is then closed back to the
initial state and its area evaluated by polygon integration — a direct measure of specific work.

The atmosphere table covers 4–14 km (`P, T, a`), so the cycle can be solved for take-off through
altitude.

## MIPCC variant

`turbojet_cycle_mipcc/` models **mass injection pre-compressor cooling**: a coolant is injected ahead of
the compressor, adding a `2 → 2c` segment with its own mixture properties and a higher effective
pressure ratio. The point of the model is that pre-compressor cooling raises the usable pressure ratio
at high flight Mach numbers, which is one of the routes to Mach 3+ air-breathing flight.

`al31_cycle/` holds a hand-computed reference cycle (AL-31 class engine) used to validate the solver,
and `compare_cycles.py` plots the two cycles against each other.

## Layout

```
engine-cycle-sim/
├─ turbojet_cycle/
│  ├─ engine_data.py         # component parameters, atmosphere, station equations
│  ├─ cycle_area.py          # T–s diagram geometry and cycle area
│  ├─ animate_cycle.py       # animated T–s build-up (writes mp4)
│  ├─ interactive_plot.py    # interactive Matplotlib exploration
│  └─ precompute_cache.py    # pre-computes station data into a pickle cache
├─ turbojet_cycle_mipcc/     # same, with pre-compressor cooling
├─ al31_cycle/               # reference AL-31 cycle for validation
├─ compare_cycles.py         # side-by-side cycle comparison
└─ docs/                     # rendered animations
```

## Quick start

```bash
pip install -r requirements.txt

cd turbojet_cycle
python precompute_cache.py     # build the station cache
python cycle_area.py           # T–s diagram + cycle area
python animate_cycle.py        # animation -> cycle_animation_sync.mp4
python interactive_plot.py     # interactive view
```

Then the MIPCC variant:

```bash
cd ../turbojet_cycle_mipcc
python precompute_cache.py
python cycle_area.py
python animate.py
```

Rendered examples: `docs/cycle_animation.mp4`, `docs/cycle_animation_mipcc.mp4`.

## Notes and limitations

* Constant `cp` per gas group (air / combustion products) — no temperature-dependent thermochemistry.
* No pressure-loss correlations beyond the fixed recovery coefficients listed above.
* The solver is a design-point cycle analysis: no off-design compressor or turbine maps.
* `engine_data.py` exists twice with different parameter sets — that is intentional, one per variant.

## Stack

Python 3.10+ · NumPy · Matplotlib (including `animation`)
