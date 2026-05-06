#!/usr/bin/env python3
"""
photosphere_spectrum.py

Compute the photosphere radiation spectrum based on the Deng & Zhang (2014)
fireball model under the simplest assumptions:

  - Impulsive Injection (single shell injected at t=0)
  - Outer Boundary at Infinity (unbounded ejecta)
  - Blackbody Distribution of Photons (Planckian in the comoving frame)

The script calculates the observed flux density F_nu (in mJy) as a function
of frequency (in Hz), prints the data in two columns, and saves a log-log
spectral plot as photosphere_spectrum.png.

Reference: Deng & Zhang (2014), ApJ, 783, L35
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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

# ---------------------------------------------------------------------------
# 1. Photosphere radius  (coasting phase, Γ = η = const)
#    τ(r_ph) = 1  ⇒  r_ph = L σ_T / (4π m_p c^3 η^3)
# ---------------------------------------------------------------------------
r_ph = L_ISO * SIGMA_T / (4.0 * np.pi * M_PROTON * C_LIGHT**3 * ETA**3)

# ---------------------------------------------------------------------------
# 2. Saturation radius  r_s = η · r0
#    Verify that the photosphere lies in the coasting phase (r_ph > r_s).
# ---------------------------------------------------------------------------
r_sat = ETA * R0

# ---------------------------------------------------------------------------
# 3. Comoving temperature at the photosphere
#    L = 4π r_ph^2 · a T'_ph^4 · η^2 · c   (energy-flux conservation)
#    ⇒  T'_ph = [L / (4π r_ph^2 a η^2 c)]^{1/4}
# ---------------------------------------------------------------------------
t_comoving = (L_ISO / (4.0 * np.pi * r_ph**2 * A_RAD * ETA**2 * C_LIGHT))**0.25

# ---------------------------------------------------------------------------
# 4. Characteristic (peak) frequency in the observer frame
#    ν_char = 2 η k T'_ph / (h (1+z))
#    where 2η ≈ D is the on-axis Doppler factor for Γ ≫ 1.
#    The factor (1+z) accounts for cosmological redshift.
# ---------------------------------------------------------------------------
nu_char = 2.0 * ETA * K_BOLTZ * t_comoving / (H_PLANCK * (1.0 + REDSHIFT))

# ---------------------------------------------------------------------------
# 5. Normalisation prefactor for the flux density
#    F_ν = C_norm · ν^3 / [exp(ν / ν_char) - 1]
#    C_norm = (r_ph / D_L)^2 · 2π h (1+z)^3 / c^2
# ---------------------------------------------------------------------------
c_norm = (r_ph / D_LUM)**2 * 2.0 * np.pi * H_PLANCK * (1.0 + REDSHIFT)**3 / C_LIGHT**2

# ---------------------------------------------------------------------------
# 6. Frequency grid  (log-spaced, spanning the observable spectrum)
# ---------------------------------------------------------------------------
N_POINTS = 500
nu_min = nu_char * 1.0e-3
nu_max = nu_char * 1.0e2
nu_grid = np.logspace(np.log10(nu_min), np.log10(nu_max), N_POINTS)

# ---------------------------------------------------------------------------
# 7. Flux density calculation
# ---------------------------------------------------------------------------
exponent = nu_grid / nu_char
# Avoid overflow for very large arguments
with np.errstate(over="ignore"):
    f_nu_cgs = c_norm * nu_grid**3 / (np.exp(exponent) - 1.0)

# Convert to mJy
f_nu_mjy = f_nu_cgs / MJY_TO_CGS

# ---------------------------------------------------------------------------
# 8. Print two-column output: frequency (Hz)  F_nu (mJy)
# ---------------------------------------------------------------------------
print("# photosphere_spectrum.py  —  Deng & Zhang (2014) impulsive-injection model")
print("# frequency (Hz)    F_nu (mJy)")
for nu, fnu in zip(nu_grid, f_nu_mjy):
    print(f"{nu:.6e}  {fnu:.6e}")

# ---------------------------------------------------------------------------
# 9. Plot log-log spectrum and save as photosphere_spectrum.png
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))

ax.loglog(nu_grid, f_nu_mjy, "b-", linewidth=1.2, label="Photosphere spectrum")

# Mark the characteristic frequency
idx_peak = np.argmax(f_nu_mjy)
ax.axvline(nu_grid[idx_peak], color="red", linestyle="--", alpha=0.6,
           label=f"ν_char ≈ {nu_char:.2e} Hz")

ax.set_xlabel("Frequency ν [Hz]", fontsize=12)
ax.set_ylabel("Flux density F_ν [mJy]", fontsize=12)
ax.set_title("Photosphere Radiation Spectrum\n"
             "Deng & Zhang (2014): Impulsive Injection, "
             "Outer Boundary at ∞, Blackbody Photons",
             fontsize=11)
ax.legend(fontsize=9)
ax.grid(True, which="both", alpha=0.25)

fig.tight_layout()
fig.savefig("photosphere_spectrum.png", dpi=150)
plt.close(fig)

# ---------------------------------------------------------------------------
# 10. Summary diagnostics (printed to stderr so stdout stays clean)
# ---------------------------------------------------------------------------
import sys
print(f"Photosphere radius:        r_ph = {r_ph:.3e} cm", file=sys.stderr)
print(f"Saturation radius:         r_s  = {r_sat:.3e} cm", file=sys.stderr)
print(f"r_ph > r_s?                {r_ph > r_sat}", file=sys.stderr)
print(f"Comoving temperature:      T'   = {t_comoving:.3e} K  "
      f"({K_BOLTZ * t_comoving / 1.602e-9:.2f} keV)", file=sys.stderr)
print(f"Characteristic frequency:  ν_char = {nu_char:.3e} Hz  "
      f"({H_PLANCK * nu_char / 1.602e-9:.2f} keV)", file=sys.stderr)
print(f"Peak flux density:         F_ν,peak = {f_nu_mjy[idx_peak]:.3e} mJy  "
      f"at ν = {nu_grid[idx_peak]:.3e} Hz", file=sys.stderr)
print(f"Spectrum plot saved to photosphere_spectrum.png", file=sys.stderr)
