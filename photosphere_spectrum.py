#!/usr/bin/env python3
"""
photosphere_spectrum.py

Compute the photosphere radiation spectrum based on the Deng & Zhang (2014,
ApJ, 785, 112) fireball model, Section 3.1, Eq.7 (original model, z=0).

Key physical ingredients:
  1. Beloborodov (2011) 2D probability density:
     P(r, μ) ∝ D² · (r_ph/r²) · exp(−r_ph/r)
     with Doppler factor D(μ) = 1 / [Γ (1 − βμ)].
  2. Observer-frame temperature (Doppler-boosted from adiabatic cooling):
     T_obs(r, μ) = T_comoving(r) · D(μ),
     T_comoving(r) = T_ph · (r / r_ph)^{−2/3}.
  3. Observer-frame Planck function B_ν(ν_obs, T_obs) — no comoving-frame
     frequency or temperature is ever substituted into the Planck formula.
  4. Cosmological redshift is set to zero (as in the original DZ14 §3.1
     derivation) — no (1+z) factors.

The δ-function constraint
    t_obs = r · (1 − β μ) / (β c)                    (z = 0)
eliminates the μ = cosθ variable analytically, reducing the (r, μ) double
integral of DZ14 Eq.7 to a single r-integral over [r_min, r_max] where
|μ_r| ≤ 1:

    F_ν(t_obs) ∝ ∫ dr  P(r, μ_r) · B_ν(ν_obs, T_obs(r, μ_r)) / r

The r-integral is evaluated numerically via scipy.integrate.quad.
Output: frequency (Hz) and flux density F_nu (mJy), plus a log-log spectral
plot saved as photosphere_spectrum.png.

References:
  Deng & Zhang (2014), ApJ, 785, 112, §3.1 Eq.7
  Beloborodov (2011), ApJ, 737, 68
"""

import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import quad  # required for δ-reduced single-integral (DZ14 Eq.7)


# ---------------------------------------------------------------------------
# Physical constants (CGS units: cm, g, s, erg, K)
# ---------------------------------------------------------------------------
C_LIGHT = 2.99792458e10      # speed of light [cm/s]
H_PLANCK = 6.62607015e-27    # Planck constant [erg s]
K_BOLTZ = 1.380649e-16       # Boltzmann constant [erg/K]
SIGMA_SB = 5.670374419e-5    # Stefan-Boltzmann constant [erg/cm^2/s/K^4]
SIGMA_T = 6.6524587321e-25   # Thomson cross section [cm^2]
M_PROTON = 1.67262192369e-24 # proton mass [g]
A_RAD = 4.0 * SIGMA_SB / C_LIGHT  # radiation constant [erg/cm^3/K^4]

# Conversion: 1 mJy = 1e-26 erg/s/cm^2/Hz
MJY_TO_CGS = 1.0e-26

# ---------------------------------------------------------------------------
# GRB / fireball parameters (illustrative values for a typical GRB)
# ---------------------------------------------------------------------------
L_ISO = 1.0e52          # isotropic-equivalent luminosity [erg/s]
ETA = 300.0              # dimensionless entropy / terminal Lorentz factor
R0 = 1.0e7               # base radius of the fireball [cm]
# Redshift is set to 0 following the DZ14 §3.1 original derivation,
# which ignores redshift effects on frequency and time.
# When z ≠ 0, insert (1+z) factors in t_obs, ν_obs, and integration limits.
REDSHIFT = 0.0           # cosmological redshift (z=0 per DZ14 §3.1)
# Luminosity distance for z=0 — use a nominal nearby distance for illustration.
# The spectral shape is independent of d_L; only the absolute flux scale depends on it.
D_LUM = 1.0e28           # luminosity distance [cm]  (~ 3.2 Gpc, nominal)

# NumPy version compatibility for trapezoidal integration
_trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))


def main():
    """Compute the DZ14 §3.1 photosphere spectrum (Beloborodov 2011 P(r,μ), observer-frame temperature)."""
    # -----------------------------------------------------------------------
    # 1. Photosphere radius  (coasting phase, Γ = η = const)
    #    τ(r_ph) = 1  ⇒  r_ph = L σ_T / (4π m_p c^3 η^3)
    #    Deng & Zhang (2014) Eq.2
    # -----------------------------------------------------------------------
    r_ph = L_ISO * SIGMA_T / (4.0 * np.pi * M_PROTON * C_LIGHT**3 * ETA**3)

    # -----------------------------------------------------------------------
    # 2. Saturation radius  r_s = η · r0
    #    Verify that the photosphere lies in the coasting phase (r_ph > r_s).
    # -----------------------------------------------------------------------
    r_sat = ETA * R0

    # -----------------------------------------------------------------------
    # 3. Comoving temperature at the photosphere
    #    L = 4π r_ph^2 · a T'_ph^4 · η^2 · c   (energy-flux conservation)
    #    ⇒  T'_ph = [L / (4π r_ph^2 a η^2 c)]^{1/4}
    # -----------------------------------------------------------------------
    T_ph_comoving = (L_ISO / (4.0 * np.pi * r_ph**2 * A_RAD * ETA**2 * C_LIGHT))**0.25

    # -----------------------------------------------------------------------
    # 4. Shell speed β derived from the terminal Lorentz factor η = Γ
    # -----------------------------------------------------------------------
    beta = np.sqrt(1.0 - 1.0 / ETA**2)

    # -----------------------------------------------------------------------
    # 5. Observer time t_obs
    #    t_obs = r_ph / (η · c)   (z = 0 per DZ14 §3.1 assumption)
    # -----------------------------------------------------------------------
    t_obs = r_ph / (ETA * C_LIGHT)

    # -----------------------------------------------------------------------
    # 6. Integration limits from the kinematic constraint |μ_r| ≤ 1
    #    μ_r(r) = (1 − t_obs·β c / r) / β
    #    μ_r ≥ -1  ⇒  r ≥ t_obs·β c / (1+β)  =: r_min
    #    μ_r ≤ +1  ⇒  r ≤ t_obs·β c / (1−β)  =: r_max
    # -----------------------------------------------------------------------
    r_min = t_obs * beta * C_LIGHT / (1.0 + beta)
    r_max = t_obs * beta * C_LIGHT / (1.0 - beta)
    # Clamp to coasting-phase validity range.
    r_min = max(r_min, r_sat)

    # -----------------------------------------------------------------------
    # 7. δ-function root — direction cosine μ as a function of radius
    #    μ_r(r) = (1 − t_obs·β c / r) / β          (z = 0)
    # -----------------------------------------------------------------------
    def mu_r(r):
        """Direction cosine μ = cosθ at radius r from the δ-function constraint (z=0)."""
        return (1.0 - t_obs * beta * C_LIGHT / r) / beta

    # -----------------------------------------------------------------------
    # 8. Doppler factor  D(μ) = 1 / [Γ (1 − β μ)]
    #    Γ = η in the coasting phase.
    #    Beloborodov (2011), Eq.(2)
    # -----------------------------------------------------------------------
    def doppler_factor(mu):
        """Doppler factor D(μ) = 1 / [Γ (1 − βμ)]."""
        return 1.0 / (ETA * (1.0 - beta * mu))

    # -----------------------------------------------------------------------
    # 9. Comoving temperature — adiabatic cooling T'_comoving(r) ∝ r^{−2/3}
    #    In the radiation-dominated coasting phase the comoving temperature
    #    drops as the fireball expands.
    # -----------------------------------------------------------------------
    def T_comoving(r):
        """Comoving temperature [K] at radius r (adiabatic cooling)."""
        return T_ph_comoving * (r / r_ph)**(-2.0 / 3.0)

    # -----------------------------------------------------------------------
    # 10. Observer-frame temperature  T_obs(r, μ) = T_comoving(r) · D(μ)
    #     Temperature transforms as T_obs = T' · D (Doppler boost).
    #     Deng & Zhang (2014) §3.1 — observer-frame temperature used directly
    #     in the Planck function with observer-frame frequency.
    # -----------------------------------------------------------------------
    def T_obs(r, mu):
        """Observer-frame temperature [K] including Doppler boost."""
        return T_comoving(r) * doppler_factor(mu)

    # -----------------------------------------------------------------------
    # 11. Beloborodov (2011) probability density P(r, μ)
    #     P(r, μ) ∝ D² · |dτ/dr| · exp(−τ)
    #     In the coasting phase: τ(r) = r_ph/r, |dτ/dr| = r_ph/r²
    #     ⇒  P(r, μ) ∝ D² · (r_ph/r²) · exp(−r_ph/r)
    #     Beloborodov (2011), ApJ, 737, 68, Eq.(8)
    #     Deng & Zhang (2014), Eq.(5)
    # -----------------------------------------------------------------------
    def P_beloborodov(r, mu):
        """Beloborodov (2011) unnormalised probability density P(r, μ) at (r, μ)."""
        exponent = -r_ph / max(r, 1e-3 * r_ph)
        if not np.isfinite(exponent):
            return 0.0
        D = doppler_factor(mu)
        return D**2 * r_ph / r**2 * np.exp(exponent)

    # -----------------------------------------------------------------------
    # 12. Planck function (specific intensity) in the OBSERVER frame
    #     B_ν(ν, T) = (2 h ν^3 / c^2) / (exp(h ν / k T) − 1)
    #     Both ν and T are observer-frame quantities — no comoving transform.
    # -----------------------------------------------------------------------
    def planck_nu(nu, T):
        """Planck specific intensity [erg/s/cm^2/Hz/sr] (observer-frame)."""
        if nu <= 0.0 or T <= 0.0:
            return 0.0
        x = H_PLANCK * nu / (K_BOLTZ * T)
        if x > 700.0:
            return 0.0
        return (2.0 * H_PLANCK * nu**3 / C_LIGHT**2) / np.expm1(x)

    # -----------------------------------------------------------------------
    # 13. Integrand for the δ-function-reduced single r-integral
    #     DZ14 Eq.7 with Beloborodov P(r,μ) and observer-frame T:
    #
    #     F_ν ∝ ∫_{r_min}^{r_max} dr  P(r, μ_r) · B_ν(ν, T_obs(r, μ_r)) / r
    #
    #     The factor 1/r comes from the Jacobian |∂t/∂μ|^{-1} = c/r
    #     of the δ-function transformation (constant c absorbed into
    #     the bolometric normalisation).
    # -----------------------------------------------------------------------
    def integrand(r, nu_obs):
        """Integrand for the δ-reduced r-integral at observer frequency nu_obs [Hz]."""
        if r < r_min or r > r_max:
            return 0.0
        mu = mu_r(r)
        if mu < -1.0 or mu > 1.0:
            return 0.0
        Tobs = T_obs(r, mu)
        P_val = P_beloborodov(r, mu)
        B_val = planck_nu(nu_obs, Tobs)  # observer-frame ν and T directly
        if B_val <= 0.0 or P_val <= 0.0:
            return 0.0
        return P_val * B_val / r

    # -----------------------------------------------------------------------
    # 14. Frequency grid  (log-spaced, spanning the observable spectrum)
    # -----------------------------------------------------------------------
    N_POINTS = 500
    nu_char_est = 2.0 * ETA * K_BOLTZ * T_ph_comoving / H_PLANCK
    nu_min = nu_char_est * 1.0e-3
    nu_max = nu_char_est * 1.0e2
    nu_grid = np.logspace(np.log10(nu_min), np.log10(nu_max), N_POINTS)

    # -----------------------------------------------------------------------
    # 15. Flux density calculation — numerical 1D integration
    #     For each frequency, integrate over radius using scipy.integrate.quad.
    # -----------------------------------------------------------------------
    print("# Computing DZ14 §3.1 photosphere spectrum "
          "(Beloborodov P(r,μ), observer-frame T) ...",
          flush=True)

    f_nu_raw = np.zeros(N_POINTS)
    for i, nu in enumerate(nu_grid):
        result, _ = quad(integrand, r_min, r_max, args=(nu,),
                         limit=200, epsabs=1e-30, epsrel=1e-6)
        f_nu_raw[i] = max(result, 0.0)

    # -- Normalisation -----------------------------------------------------
    # Scale the raw integral so that the bolometric flux matches the
    # isotropic equivalent luminosity: ∫ F_ν dν ≈ L_ISO/(4π d_L²)
    # (z = 0, no (1+z) factor in the bolometric flux formula).
    bol_raw = _trapz(f_nu_raw, nu_grid)
    F_bol_expected = L_ISO / (4.0 * np.pi * D_LUM**2)
    norm_factor = F_bol_expected / bol_raw if bol_raw > 0 else 1.0

    f_nu_cgs = f_nu_raw * norm_factor
    f_nu_mjy = f_nu_cgs / MJY_TO_CGS

    # -----------------------------------------------------------------------
    # 16. Characteristic frequency from the integrated spectrum (peak of F_ν)
    # -----------------------------------------------------------------------
    idx_peak = np.argmax(f_nu_mjy)
    nu_char = nu_grid[idx_peak]

    # -----------------------------------------------------------------------
    # 17. Print two-column output: frequency (Hz)  F_nu (mJy)
    # -----------------------------------------------------------------------
    print("# photosphere_spectrum.py  —  DZ14 §3.1 Beloborodov (2011) model")
    print("# frequency (Hz)    F_nu (mJy)")
    for nu, fnu in zip(nu_grid, f_nu_mjy):
        print(f"{nu:.6e}  {fnu:.6e}")

    # -----------------------------------------------------------------------
    # 18. Plot log-log spectrum and save as photosphere_spectrum.png
    # -----------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.loglog(nu_grid, f_nu_mjy, "b-", linewidth=1.2,
              label="DZ14 §3.1: Beloborodov P(r,μ), obs-frame T")

    ax.axvline(nu_char, color="red", linestyle="--", alpha=0.6,
               label=f"ν_peak ≈ {nu_char:.2e} Hz")

    ax.set_xlabel("Frequency ν [Hz]", fontsize=12)
    ax.set_ylabel("Flux density F_ν [mJy]", fontsize=12)
    ax.set_title("Photosphere Radiation Spectrum\n"
                 "Deng & Zhang (2014) §3.1: Beloborodov P(r,μ) + Observer-Frame Temperature\n"
                 "(z=0, Impulsive Injection, ∞ Boundary, Blackbody Photons)",
                 fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, which="both", alpha=0.25)

    fig.tight_layout()
    fig.savefig("photosphere_spectrum.png", dpi=150)
    plt.close(fig)

    # -----------------------------------------------------------------------
    # 19. Summary diagnostics (printed to stderr so stdout stays clean)
    # -----------------------------------------------------------------------
    print(f"Photosphere radius:        r_ph = {r_ph:.3e} cm",
          file=sys.stderr)
    print(f"Saturation radius:         r_s  = {r_sat:.3e} cm",
          file=sys.stderr)
    print(f"r_ph > r_s?                {r_ph > r_sat}",
          file=sys.stderr)
    print(f"Shell speed:               β    = {beta:.6f}",
          file=sys.stderr)
    print(f"Lorentz factor:            Γ    = {ETA:.1f}",
          file=sys.stderr)
    print(f"Observer time:             t_obs = {t_obs:.3e} s",
          file=sys.stderr)
    print(f"Integration limits:        r ∈ [{r_min:.3e}, {r_max:.3e}] cm",
          file=sys.stderr)
    print(f"Comoving temperature:      T'_ph = {T_ph_comoving:.3e} K  "
          f"({K_BOLTZ * T_ph_comoving / 1.602e-9:.2f} keV)",
          file=sys.stderr)
    print(f"Redshift:                  z = {REDSHIFT}  (DZ14 §3.1 ignores redshift)",
          file=sys.stderr)
    print(f"Peak frequency:            ν_peak = {nu_char:.3e} Hz  "
          f"({H_PLANCK * nu_char / 1.602e-9:.2f} keV)",
          file=sys.stderr)
    print(f"Peak flux density:         F_ν,peak = {f_nu_mjy[idx_peak]:.3e} mJy  "
          f"at ν = {nu_grid[idx_peak]:.3e} Hz",
          file=sys.stderr)
    print("Spectrum plot saved to photosphere_spectrum.png",
          file=sys.stderr)

    # -----------------------------------------------------------------------
    # 20. Modification summary
    # -----------------------------------------------------------------------
    print("\n# === Modification Summary ===", file=sys.stderr)
    print("# 1. P(r,μ): Beloborodov (2011) D^2 · (r_ph/r^2) · exp(-r_ph/r) "
          "(was: simple r_ph/r^2 · exp(-r_ph/r))", file=sys.stderr)
    print("# 2. Temperature: observer-frame T_obs = T_comoving · D(μ) "
          "(was: comoving T in Planck)", file=sys.stderr)
    print("# 3. Frequency: observer-frame ν directly in Planck "
          "(was: comoving ν' transformed)", file=sys.stderr)
    print("# 4. Redshift: z = 0 (was: z = 1.0); all (1+z) factors removed "
          "per DZ14 §3.1", file=sys.stderr)


if __name__ == "__main__":
    main()
