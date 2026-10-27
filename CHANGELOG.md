# Changelog

## 1.0.0 - 2026-10-27

First public release.

- Numerical solution of the driven series RLC equation with `scipy.integrate.solve_ivp`
- Closed-form solution for underdamped, critically damped and overdamped circuits
- Damping sweep, error plot and resonance curves
- `--defaults` and `--outdir` command line options for non-interactive runs
- Test suite covering all three damping regimes and the resonance behaviour
