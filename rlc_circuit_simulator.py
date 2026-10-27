import argparse
import copy
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

plt.switch_backend("Agg")

NAVY, RUST, GREEN, GOLD, GREY = "#1F3A5F", "#B5472E", "#2E8B6E", "#C9962B", "#6B7785"
PALETTE = [RUST, NAVY, GREEN, GOLD, GREY, "#7A4E9C"]

DEFAULTS = {
    "L": 1.0,
    "R": 2.0,
    "C": 0.25,
    "E0": 10.0,
    "w": 3.0,
    "t_end": 12.0,
    "R_sweep": [0.4, 2.0, 4.0, 8.0],
    "R_res": [0.4, 2.0, 4.0],
    "w_pts": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5],
}


def ask_float(label, default, positive=True):
    while True:
        raw = input(f"{label} [default {default}]: ").strip()
        if raw == "":
            return float(default)
        try:
            val = float(raw)
        except ValueError:
            print("  Please enter a number.")
            continue
        if positive and val <= 0:
            print("  Value must be greater than zero.")
            continue
        return val


def ask_list(label, default):
    while True:
        raw = input(f"{label} [default {', '.join(str(d) for d in default)}]: ").strip()
        if raw == "":
            return list(default)
        try:
            vals = [float(x) for x in raw.replace(",", " ").split()]
        except ValueError:
            print("  Please enter numbers separated by commas or spaces.")
            continue
        if vals and all(v > 0 for v in vals):
            return vals
        print("  All values must be greater than zero.")


def get_parameters():
    print("Series RLC circuit:  L q'' + R q' + q/C = E0 cos(w t)")
    print("Press Enter to keep the default value.\n")
    d = DEFAULTS
    p = {}
    p["L"] = ask_float("Inductance L (H)", d["L"])
    p["R"] = ask_float("Resistance R (ohm)", d["R"])
    p["C"] = ask_float("Capacitance C (F)", d["C"])
    p["E0"] = ask_float("Source amplitude E0 (V)", d["E0"])
    p["w"] = ask_float("Forcing frequency w (rad/s)", d["w"])
    p["t_end"] = ask_float("Simulation end time (s)", d["t_end"])
    p["R_sweep"] = ask_list("Resistances for damping sweep (ohm)", d["R_sweep"])
    p["R_res"] = ask_list("Resistances for resonance curves (ohm)", d["R_res"])
    p["w_pts"] = ask_list("Frequencies for simulated resonance points (rad/s)", d["w_pts"])
    return p


def coefficients(p):
    a = p["R"] / p["L"]
    b = 1 / (p["L"] * p["C"])
    F = p["E0"] / p["L"]
    return a, b, F


def particular(a, b, F, w):
    M = np.array([[b - w**2, a * w],
                  [-a * w, b - w**2]])
    return np.linalg.solve(M, [F, 0.0])


def analytic(t, a, b, F, w):
    Ap, Bp = particular(a, b, F, w)
    qp = Ap * np.cos(w * t) + Bp * np.sin(w * t)
    disc = a**2 / 4 - b
    sigma = a / 2
    if disc < -1e-12:
        wd = np.sqrt(-disc)
        C1 = -Ap
        C2 = (sigma * C1 - w * Bp) / wd
        qh = np.exp(-sigma * t) * (C1 * np.cos(wd * t) + C2 * np.sin(wd * t))
    elif abs(disc) <= 1e-12:
        C1 = -Ap
        C2 = sigma * C1 - w * Bp
        qh = (C1 + C2 * t) * np.exp(-sigma * t)
    else:
        r1, r2 = -sigma + np.sqrt(disc), -sigma - np.sqrt(disc)
        C2 = (-w * Bp + r1 * Ap) / (r2 - r1)
        C1 = -Ap - C2
        qh = C1 * np.exp(r1 * t) + C2 * np.exp(r2 * t)
    return qh + qp


def rhs(t, y, a, b, F, w):
    q, i = y
    return [i, F * np.cos(w * t) - a * i - b * q]


def simulate(t, y0, a, b, F, w):
    sol = solve_ivp(rhs, (t[0], t[-1]), y0, t_eval=t, rtol=1e-9, atol=1e-12,
                    args=(a, b, F, w))
    return sol.y[0]


def classify(R, L, C):
    d = R**2 - 4 * L / C
    if d < -1e-9:
        return "underdamped"
    return "critically damped" if abs(d) <= 1e-9 else "overdamped"


def damping_ratio(R, L, C):
    return R / (2 * np.sqrt(L / C))


def free_response(t, p, b):
    out = {}
    for R in p["R_sweep"]:
        out[R] = simulate(t, [1.0, 0.0], R / p["L"], b, 0.0, p["w"])
        print(f"R = {R:>6} ohm  zeta = {damping_ratio(R, p['L'], p['C']):.2f}  "
              f"{classify(R, p['L'], p['C'])}")
    return out


def amplitude(w, a, b, F):
    return F / np.sqrt((b - w**2)**2 + (a * w)**2)


def simulated_amplitude(w, a, b, F):
    T = 2 * np.pi / w
    t_stop = max(40.0, 30 * T)
    tt = np.linspace(0, t_stop, int(t_stop * 200))
    q = simulate(tt, [0.0, 0.0], a, b, F, w)
    return np.abs(q[tt > t_stop - 2 * T]).max()


def style_plots():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": GREY, "axes.grid": True,
                         "grid.color": "#E3E7EB", "grid.linewidth": .7})


def plot_overlay(t, q_ana, q_num, outdir):
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    ax.plot(t, q_ana, color=NAVY, lw=2.4, label="analytical")
    ax.plot(t[::12], q_num[::12], "o", color=RUST, ms=4.5, label="solve_ivp")
    ax.set(xlabel="t (s)", ylabel="q (C)")
    ax.legend(frameon=False, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.13))
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "fig_overlay.png"), dpi=220)
    plt.close(fig)


def plot_error(t, err, outdir):
    fig, ax = plt.subplots(figsize=(4.0, 3.3))
    ax.semilogy(t, err + 1e-16, color=RUST, lw=1.6)
    ax.set(xlabel="t (s)", ylabel="|error| (C)")
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "fig_error.png"), dpi=220)
    plt.close(fig)


def plot_sweep(t, free, p, outdir):
    fig, ax = plt.subplots(figsize=(6.0, 3.3))
    for k, (R, y) in enumerate(free.items()):
        z = damping_ratio(R, p["L"], p["C"])
        ax.plot(t, y, color=PALETTE[k % len(PALETTE)], lw=2, label=f"R = {R} ohm, zeta = {z:.2f}")
    ax.axhline(0, color=GREY, lw=.8)
    ax.set(xlabel="t (s)", ylabel="q (C)")
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "fig_sweep.png"), dpi=220)
    plt.close(fig)


def plot_resonance(ws, p, a, b, F, outdir):
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    for k, R in enumerate(p["R_res"]):
        ax.plot(ws, amplitude(ws, R / p["L"], b, F), color=PALETTE[k % len(PALETTE)], lw=2,
                label=f"R = {R} ohm")
    wp = np.array(p["w_pts"])
    ax.plot(wp, [simulated_amplitude(x, a, b, F) for x in wp], "o", color="k", ms=4,
            label=f"simulated, R = {p['R']}")
    ax.set(xlabel="forcing frequency (rad/s)", ylabel="steady-state |q| (C)")
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, "fig_resonance.png"), dpi=220)
    plt.close(fig)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Driven series RLC circuit simulator.")
    parser.add_argument("--defaults", action="store_true",
                        help="skip the prompts and use the default parameters")
    parser.add_argument("--outdir", default=".",
                        help="folder for the figures and results.json (default: current folder)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    os.makedirs(args.outdir, exist_ok=True)

    p = copy.deepcopy(DEFAULTS) if args.defaults else get_parameters()
    a, b, F = coefficients(p)
    w = p["w"]

    t = np.linspace(0, p["t_end"], 600)
    q_num = simulate(t, [0.0, 0.0], a, b, F, w)
    q_ana = analytic(t, a, b, F, w)
    err = np.abs(q_num - q_ana)
    print("\nmax |q_num - q_ana| =", err.max())
    print(f"Chosen circuit is {classify(p['R'], p['L'], p['C'])}\n")

    free = free_response(t, p, b)

    style_plots()
    plot_overlay(t, q_ana, q_num, args.outdir)
    plot_error(t, err, args.outdir)
    plot_sweep(t, free, p, args.outdir)

    w_hi = max(4.0, 1.5 * max(p["w_pts"] + [w]))
    ws = np.linspace(0.2, w_hi, 400)
    plot_resonance(ws, p, a, b, F, args.outdir)

    Ap, Bp = particular(a, b, F, w)
    res = dict(max_err=float(err.max()), Ap=float(Ap), Bp=float(Bp),
               amp=float(amplitude(w, a, b, F)),
               sim_amp=float(simulated_amplitude(w, a, b, F)),
               peak_w=float(ws[np.argmax(amplitude(ws, min(p["R_res"]) / p["L"], b, F))]))
    with open(os.path.join(args.outdir, "results.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(res)


if __name__ == "__main__":
    main()
