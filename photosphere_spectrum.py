#!/usr/bin/env python3
"""
photosphere_spectrum.py

Compute the photosphere radiation spectrum based on the Deng & Zhang (2014)
fireball model using the δ-function-reduced single-integral formalism
(DZ14 Eq.7).

The δ-function constraint
    t_obs = r · (1 − β μ) / (β c (1+z))
is used to eliminate the μ = cosθ variable analytically, collapsing the
(r, μ) double integral into a single r-integral over [r_min, r_max] where
|μ_r| ≤ 1:

    F_ν(t_obs) ∝ ∫ dr  P(r) · P_ν(ν'(r), T'(r)) / r

with
    μ_r(r) = (1 − t_obs·β c·(1+z) / r) / β          (δ-function root)
    ν'(r)  = ν_obs · (1+z) · (1 − β μ_r(r))         (comoving frequency)
    T'(r)  = T'_ph · (r / r_ph)^{−2/3}              (adiabatic cooling)
    P(r)   ∝ r^{−2} · exp(−r_ph / r)               (last-scattering PDF)

The r-integral is evaluated numerically via scipy.integrate.quad.
The output captures the non-Planckian low-energy slope (ν or ν² power-law
from Doppler-boost superposition) and the steepened high-energy tail from
adiabatic cooling.

The script prints frequency (Hz) and flux density F_nu (mJy) in two columns,
and saves a log-log spectral plot as photosphere_spectrum.png.

Reference: Deng & Zhang (2014), ApJ, 783, L35
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
REDSHIFT = 1.0           # cosmological redshift
# Luminosity distance for z=1 with standard ΛCDM (H0=70, Ωm=0.3, ΩΛ=0.7)
D_LUM = 2.04e28          # luminosity distance [cm]  (~ 6.6 Gpc)

# NumPy version compatibility for trapezoidal integration
_trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))


def main():
    """Compute the δ-reduced single-integral photosphere spectrum."""
    # -----------------------------------------------------------------------
    # 1. Photosphere radius  (coasting phase, Γ = η = const)
    #    τ(r_ph) = 1  ⇒  r_ph = L σ_T / (4π m_p c^3 η^3)
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
    T_ph = (L_ISO / (4.0 * np.pi * r_ph**2 * A_RAD * ETA**2 * C_LIGHT))**0.25

    # -----------------------------------------------------------------------
    # 4. Shell speed β derived from the terminal Lorentz factor η
    # -----------------------------------------------------------------------
    beta = np.sqrt(1.0 - 1.0 / ETA**2)

    # -----------------------------------------------------------------------
    # 5. Observer time t_obs
    #    Choose t_obs so that r_ph lies near the geometric mean of the
    #    integration limits → t_obs = r_ph / (η · c · (1+z)).
    # -----------------------------------------------------------------------
    t_obs = r_ph / (ETA * C_LIGHT * (1.0 + REDSHIFT))

    # -----------------------------------------------------------------------
    # 6. Integration limits from the kinematic constraint |μ_r| ≤ 1
    #    μ_r(r) = (1 − t_obs·β c·(1+z) / r) / β
    #    μ_r ≥ -1  ⇒  r ≥ t_obs·β c·(1+z) / (1+β)  =: r_min
    #    μ_r ≤ +1  ⇒  r ≤ t_obs·β c·(1+z) / (1−β)  =: r_max
    # -----------------------------------------------------------------------
    r_min = t_obs * beta * C_LIGHT * (1.0 + REDSHIFT) / (1.0 + beta)
    r_max = t_obs * beta * C_LIGHT * (1.0 + REDSHIFT) / (1.0 - beta)
    # Guard: kinematic r_min can fall below r_sat; the integrand
    # contribution below r_sat is negligible (P(r) ≈ exp(−600) ≈ 0), but
    # we clamp to the coasting-phase validity range for physical consistency.
    r_min = max(r_min, r_sat)

    # -----------------------------------------------------------------------
    # 7. δ-function root — direction cosine μ as a function of radius
    #    μ_r(r) = (1 − t_obs·β c·(1+z) / r) / β
    # -----------------------------------------------------------------------
    def mu_r(r):
        """Direction cosine μ = cosθ at radius r from the δ-function constraint."""
        return (1.0 - t_obs * beta * C_LIGHT * (1.0 + REDSHIFT) / r) / beta

    # -----------------------------------------------------------------------
    # 8. Comoving frequency ν'(r) seen by a shell element at radius r
    #    ν'(r) = ν_obs · (1+z) · (1 − β μ_r(r))
    #    Substituting μ_r:
    #      ν'(r) = ν_obs · t_obs · β c · (1+z)^2 / r
    # -----------------------------------------------------------------------
    def nu_comoving(r, nu_obs):
        """Comoving-frame frequency [Hz] at radius r."""
        mu = mu_r(r)
        return nu_obs * (1.0 + REDSHIFT) * (1.0 - beta * mu)

    # -----------------------------------------------------------------------
    # 9. Comoving temperature — adiabatic cooling T'(r) ∝ r^{−2/3}
    #    In the radiation-dominated coasting phase the comoving temperature
    #    drops as the fireball expands.
    # -----------------------------------------------------------------------
    def temperature_comoving(r):
        """Comoving temperature [K] at radius r (adiabatic cooling)."""
        return T_ph * (r / r_ph)**(-2.0 / 3.0)

    # -----------------------------------------------------------------------
    # 10. Probability density of last scattering at radius r
    #     In the coasting phase (r > r_s) with τ(r) = r_ph / r:
    #     P(r) = |dτ/dr| · exp(−τ) = (r_ph / r^2) · exp(−r_ph / r)
    # -----------------------------------------------------------------------
    def P_last_scattering(r):
        """Unnormalised probability density of last scattering at radius r."""
        exponent = -r_ph / max(r, 1e-3 * r_ph)
        if not np.isfinite(exponent):
            return 0.0
        return r_ph / r**2 * np.exp(exponent)

    # -----------------------------------------------------------------------
    # 11. Planck function (specific intensity) in the comoving frame
    #     B_ν(ν, T) = (2 h ν^3 / c^2) / (exp(h ν / k T) − 1)
    # -----------------------------------------------------------------------
    def planck_nu(nu, T):
        """Planck specific intensity [erg/s/cm^2/Hz/sr]."""
        if nu <= 0.0 or T <= 0.0:
            return 0.0
        x = H_PLANCK * nu / (K_BOLTZ * T)
        if x > 700.0:
            return 0.0
        return (2.0 * H_PLANCK * nu**3 / C_LIGHT**2) / np.expm1(x)

    # -----------------------------------------------------------------------
    # 12. Integrand for the δ-function-reduced single r-integral
    #     integrand(r) = P(r) · B_ν(ν'(r), T'(r)) / r
    #     The factor 1/r comes from the Jacobian |dt_obs/dμ|^{-1} = c(1+z)/r
    #     of the δ-function transformation.
    # -----------------------------------------------------------------------
    def integrand(r, nu_obs):
        """Integrand for the δ-reduced r-integral at frequency nu_obs [Hz]."""
        if r < r_min or r > r_max:
            return 0.0
        nup = nu_comoving(r, nu_obs)
        T_l = temperature_comoving(r)
        P_r = P_last_scattering(r)
        B = planck_nu(nup, T_l)
        if B <= 0.0 or P_r <= 0.0:
            return 0.0
        return P_r * B / r

    # -----------------------------------------------------------------------
    # 13. Frequency grid  (log-spaced, spanning the observable spectrum)
    # -----------------------------------------------------------------------
    N_POINTS = 500
    nu_char_est = 2.0 * ETA * K_BOLTZ * T_ph / (H_PLANCK * (1.0 + REDSHIFT))
    nu_min = nu_char_est * 1.0e-3
    nu_max = nu_char_est * 1.0e2
    nu_grid = np.logspace(np.log10(nu_min), np.log10(nu_max), N_POINTS)

    # -----------------------------------------------------------------------
    # 14. Flux density calculation — numerical 1D integration
    #     For each frequency, integrate over radius using scipy.integrate.quad.
    # -----------------------------------------------------------------------
    print("# Computing δ-reduced single-integral photosphere spectrum ...",
          flush=True)

    f_nu_raw = np.zeros(N_POINTS)
    for i, nu in enumerate(nu_grid):
        result, _ = quad(integrand, r_min, r_max, args=(nu,),
                         limit=200, epsabs=1e-30, epsrel=1e-6)
        f_nu_raw[i] = max(result, 0.0)

    # -- Normalisation -----------------------------------------------------
    # Scale the raw integral so that the bolometric flux matches the
    # isotropic equivalent luminosity: ∫ F_ν dν ≈ L_ISO/(4π d_L² (1+z)).
    bol_raw = _trapz(f_nu_raw, nu_grid)
    F_bol_expected = L_ISO / (4.0 * np.pi * D_LUM**2 * (1.0 + REDSHIFT))
    norm_factor = F_bol_expected / bol_raw if bol_raw > 0 else 1.0

    f_nu_cgs = f_nu_raw * norm_factor
    f_nu_mjy = f_nu_cgs / MJY_TO_CGS

    # -----------------------------------------------------------------------
    # 15. Characteristic frequency from the integrated spectrum (peak of F_ν)
    # -----------------------------------------------------------------------
    idx_peak = np.argmax(f_nu_mjy)
    nu_char = nu_grid[idx_peak]

    # -----------------------------------------------------------------------
    # 16. Print two-column output: frequency (Hz)  F_nu (mJy)
    # -----------------------------------------------------------------------
    print("# photosphere_spectrum.py  —  Deng & Zhang (2014) δ-reduced "
          "single-integral model")
    print("# frequency (Hz)    F_nu (mJy)")
    for nu, fnu in zip(nu_grid, f_nu_mjy):
        print(f"{nu:.6e}  {fnu:.6e}")

    # -----------------------------------------------------------------------
    # 17. Plot log-log spectrum and save as photosphere_spectrum.png
    # -----------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.loglog(nu_grid, f_nu_mjy, "b-", linewidth=1.2,
              label="δ-reduced photosphere spectrum")

    ax.axvline(nu_char, color="red", linestyle="--", alpha=0.6,
               label=f"ν_peak ≈ {nu_char:.2e} Hz")

    ax.set_xlabel("Frequency ν [Hz]", fontsize=12)
    ax.set_ylabel("Flux density F_ν [mJy]", fontsize=12)
    ax.set_title("Photosphere Radiation Spectrum\n"
                 "Deng & Zhang (2014): δ-Reduced Single Integral "
                 "(Impulsive Injection, ∞ Boundary, Blackbody Photons)",
                 fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(True, which="both", alpha=0.25)

    fig.tight_layout()
    fig.savefig("photosphere_spectrum.png", dpi=150)
    plt.close(fig)

    # -----------------------------------------------------------------------
    # 18. Summary diagnostics (printed to stderr so stdout stays clean)
    # -----------------------------------------------------------------------
    print(f"Photosphere radius:        r_ph = {r_ph:.3e} cm",
          file=sys.stderr)
    print(f"Saturation radius:         r_s  = {r_sat:.3e} cm",
          file=sys.stderr)
    print(f"r_ph > r_s?                {r_ph > r_sat}",
          file=sys.stderr)
    print(f"Shell speed:               β    = {beta:.6f}",
          file=sys.stderr)
    print(f"Observer time:             t_obs = {t_obs:.3e} s",
          file=sys.stderr)
    print(f"Integration limits:        r ∈ [{r_min:.3e}, {r_max:.3e}] cm",
          file=sys.stderr)
    print(f"Comoving temperature:      T'_ph = {T_ph:.3e} K  "
          f"({K_BOLTZ * T_ph / 1.602e-9:.2f} keV)",
          file=sys.stderr)
    print(f"Peak frequency:            ν_peak = {nu_char:.3e} Hz  "
          f"({H_PLANCK * nu_char / 1.602e-9:.2f} keV)",
          file=sys.stderr)
    print(f"Peak flux density:         F_ν,peak = {f_nu_mjy[idx_peak]:.3e} mJy  "
          f"at ν = {nu_grid[idx_peak]:.3e} Hz",
          file=sys.stderr)
    print("Spectrum plot saved to photosphere_spectrum.png",
          file=sys.stderr)


if __name__ == "__main__":
    main()
