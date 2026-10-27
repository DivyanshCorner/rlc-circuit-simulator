# RLC Circuit Simulator

A small Python tool that simulates a driven series RLC circuit. It solves the equation of motion for the capacitor charge numerically, checks the result against the exact solution, and plots the damping behaviour and resonance curves.

```
L q'' + R q' + q / C = E0 cos(w t)
```

## What it does

- Integrates the circuit with `scipy.integrate.solve_ivp` (tight tolerances)
- Computes the closed-form solution for underdamped, critically damped and overdamped cases
- Reports the maximum difference between the two (about 1e-9 C with the default values)
- Sweeps the resistance to show how damping changes the free response
- Draws resonance curves and compares them with amplitudes measured from long simulations
- Saves the figures as PNG files and the key numbers to `results.json`

## Example output

| Numerical vs analytical | Error |
| :---: | :---: |
| ![Overlay](docs/fig_overlay.png) | ![Error](docs/fig_error.png) |

| Damping sweep | Resonance |
| :---: | :---: |
| ![Sweep](docs/fig_sweep.png) | ![Resonance](docs/fig_resonance.png) |

## Installation

```bash
git clone https://github.com/<DivyanshCorner/rlc-circuit-simulator.git
cd rlc-circuit-simulator
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Python 3.9 or newer is required.

## Usage

Run it and answer the prompts. Press Enter to keep a default value.

```bash
python rlc_circuit_simulator.py
```

For a non-interactive run with the defaults, writing everything to a folder:

```bash
python rlc_circuit_simulator.py --defaults --outdir out
```

### Parameters

| Prompt                       | Default                          | Meaning                                    |
| ---------------------------- | -------------------------------- | ------------------------------------------ |
| Inductance L                 | 1.0 H                            |                                            |
| Resistance R                 | 2.0 ohm                          | Circuit used for the main simulation       |
| Capacitance C                | 0.25 F                           |                                            |
| Source amplitude E0          | 10.0 V                           |                                            |
| Forcing frequency w          | 3.0 rad/s                        |                                            |
| Simulation end time          | 12.0 s                           |                                            |
| Resistances for damping sweep| 0.4, 2.0, 4.0, 8.0 ohm           | Free decay for each value                  |
| Resistances for resonance    | 0.4, 2.0, 4.0 ohm                | Theoretical amplitude curves               |
| Frequencies for simulated points | 0.5 to 3.5 rad/s             | Points measured from simulation            |

### Output files

| File                | Content                                              |
| ------------------- | ---------------------------------------------------- |
| `fig_overlay.png`   | Charge versus time, analytical and numerical         |
| `fig_error.png`     | Absolute difference between the two, log scale       |
| `fig_sweep.png`     | Free response for each resistance, with damping ratio|
| `fig_resonance.png` | Steady-state amplitude versus forcing frequency      |
| `results.json`      | Maximum error, steady-state coefficients, amplitudes, resonance peak |

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests cover the classification of damping regimes, agreement between the analytical and numerical solutions in all three regimes, the steady-state coefficients, the resonance peak and a full command line run.

## Project structure

```
rlc-circuit-simulator/
├── rlc_circuit_simulator.py
├── tests/
│   └── test_simulator.py
├── docs/
│   ├── theory.md        # derivation of the equations
│   └── fig_*.png        # figures used in this README
├── .github/workflows/tests.yml
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

The maths behind the program is written up in [docs/theory.md](docs/theory.md).

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Released under the [MIT License](LICENSE).
