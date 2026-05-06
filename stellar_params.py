#!/usr/bin/env python3
"""
Calculate main-sequence stellar parameters using empirical mass-luminosity relations.

Computes luminosity (L), effective temperature (Teff), and main-sequence
lifetime (τ_ms) for a list of stellar masses based on segmented power-law
fits to observational data.

Mass-Luminosity Relation (segmented power-law):
  Reference: Duric (2004), "Advanced Astrophysics"; Böhm-Vitense (1992),
  "Introduction to Stellar Astrophysics".
  The piecewise form used here follows the standard empirical calibration:

    M < 0.43 M☉   :  L/L☉ = 0.23 × (M/M☉)^2.3
    0.43 ≤ M < 2 M☉ :  L/L☉ = 1.0 × (M/M☉)^4.0
    2 ≤ M < 55 M☉  :  L/L☉ = 1.4 × (M/M☉)^3.5
    M ≥ 55 M☉      :  L/L☉ ≈ 32000 × (M/M☉)

Constants:
  Solar luminosity    L☉ = 3.828e26 W
  Solar mass          M☉ = 1.989e30 kg
  Solar temperature   Teff☉ = 5778 K
  Solar main-seq life τ☉ ≈ 10 Gyr

Output: printed table, CSV, and JSON (all to stdout).
"""

# ---------------------------------------------------------------------------
# Physical constants (SI, except where noted)
# ---------------------------------------------------------------------------
L_SUN = 3.828e26       # Solar luminosity (W)
T_SUN = 5778.0         # Solar effective temperature (K)
TAU_SUN = 10.0         # Solar main-sequence lifetime (Gyr)


# ---------------------------------------------------------------------------
# Mass-luminosity relation (main sequence, empirical segmented power-law)
# ---------------------------------------------------------------------------

def luminosity(m: float) -> float:
    """
    Return L/L☉ for a main-sequence star of mass m (in solar masses).

    Uses piecewise empirical power-law fits (see module docstring).
    """
    if m <= 0.0:
        raise ValueError(f"Mass must be positive, got {m}")

    if m < 0.43:
        return 0.23 * (m ** 2.3)
    elif m < 2.0:
        return 1.0 * (m ** 4.0)
    elif m < 55.0:
        return 1.4 * (m ** 3.5)
    else:
        return 32000.0 * m


def effective_temperature(l_lsun: float, m: float) -> float:
    """
    Estimate effective temperature (K) from L/L☉ and M/M☉.

    Uses Teff ∝ (L / R²)^(1/4) with radius estimated as R ∝ M^β:
      β ≈ 0.6 for M ≤ 1 M☉, β ≈ 0.8 for M > 1 M☉
    (approximate from main-sequence radius-mass relation).
    """
    beta = 0.6 if m <= 1.0 else 0.8
    r_rsun = m ** beta
    return T_SUN * (l_lsun ** 0.25) / (r_rsun ** 0.5)


def main_sequence_lifetime(l_lsun: float, m: float) -> float:
    """
    Estimate main-sequence lifetime (Gyr).

    τ_ms ≈ τ☉ × (M / L) since fuel supply ∝ M and consumption rate ∝ L.
    """
    return TAU_SUN * m / l_lsun


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def spectral_type_approx(m: float) -> str:
    """Return a rough spectral type label based on mass."""
    if m < 0.08:
        return "brown dwarf(?)"
    elif m < 0.45:
        return "M (red dwarf)"
    elif m < 0.8:
        return "K"
    elif m < 1.04:
        return "G (Sun-like)"
    elif m < 1.4:
        return "F"
    elif m < 2.1:
        return "A"
    elif m < 4.0:
        return "B"
    elif m < 16:
        return "O (early)"
    elif m < 55:
        return "O (mid)"
    else:
        return "O/WR (v. massive)"


def format_table(masses):
    """Return a formatted ASCII table with stellar parameters."""
    header = (
        f"{'M (M☉)':>8s}  "
        f"{'L (L☉)':>12s}  "
        f"{'L (W)':>12s}  "
        f"{'Teff (K)':>10s}  "
        f"{'τ_ms (Gyr)':>12s}  "
        f"{'Spectral type':>18s}"
    )
    sep = "-" * len(header)
    lines = [header, sep]

    for m in masses:
        l_lsun = luminosity(m)
        l_w = l_lsun * L_SUN
        teff = effective_temperature(l_lsun, m)
        tau = main_sequence_lifetime(l_lsun, m)
        sp = spectral_type_approx(m)
        lines.append(
            f"{m:8.3f}  "
            f"{l_lsun:12.4e}  "
            f"{l_w:12.4e}  "
            f"{teff:10.0f}  "
            f"{tau:12.4e}  "
            f"{sp:>18s}"
        )
    return "\n".join(lines)


def to_csv(masses):
    """Return CSV representation of the stellar parameters."""
    lines = ["M_Msun,L_Lsun,L_W,Teff_K,tau_ms_Gyr,spectral_type"]
    for m in masses:
        l_lsun = luminosity(m)
        l_w = l_lsun * L_SUN
        teff = effective_temperature(l_lsun, m)
        tau = main_sequence_lifetime(l_lsun, m)
        sp = spectral_type_approx(m)
        lines.append(
            f"{m:.4f},{l_lsun:.6e},{l_w:.6e},{teff:.1f},{tau:.6e},{sp}"
        )
    return "\n".join(lines)


def to_json(masses):
    """Return JSON string without external dependencies."""
    entries = []
    for m in masses:
        l_lsun = luminosity(m)
        teff = effective_temperature(l_lsun, m)
        tau = main_sequence_lifetime(l_lsun, m)
        sp = spectral_type_approx(m)
        entries.append(
            '    {{"M_Msun": {m:.4f}, "L_Lsun": {l:.6e}, '
            '"L_W": {lw:.6e}, "Teff_K": {teff:.1f}, '
            '"tau_ms_Gyr": {tau:.6e}, '
            '"spectral_type": "{sp}"}}'.format(
                m=m, l=l_lsun, lw=l_lsun * L_SUN,
                teff=teff, tau=tau, sp=sp,
            )
        )
    return "[\n" + ",\n".join(entries) + "\n]"


# ---------------------------------------------------------------------------
# Default mass grid
# ---------------------------------------------------------------------------

DEFAULT_MASSES = [
    0.1, 0.2, 0.3, 0.5, 0.8,
    1.0, 1.2, 1.5, 2.0, 3.0,
    5.0, 7.0, 10.0, 15.0, 20.0,
    30.0, 40.0, 60.0, 80.0, 100.0,
]


def main():
    """Entry point: compute and print stellar parameters for default mass grid."""
    masses = DEFAULT_MASSES

    print("=" * 84)
    print("  Main-Sequence Stellar Parameters (Mass-Luminosity Relation)")
    print("=" * 84)
    print()
    print(format_table(masses))
    print()

    print("--- CSV output ---")
    print(to_csv(masses))
    print()

    print("--- JSON output ---")
    print(to_json(masses))


if __name__ == "__main__":
    main()
