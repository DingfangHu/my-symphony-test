#!/usr/bin/env python3
"""
GRB Afterglow Light Curve Calculator (TES-30)

Computes synchrotron radiation light curves from the external forward shock
of a gamma-ray burst using the standard afterglow model based on
Granot & Sari (2002), Sari, Piran & Narayan (1998), and the
Blandford-McKee (1976) self-similar solution.

Physics:
  - Adiabatic ultra-relativistic blast wave expanding into a constant-density
    ISM (interstellar medium).
  - Synchrotron radiation from a power-law distribution of shock-accelerated
    electrons: N(gamma) ~ gamma^(-p) for gamma > gamma_m.
  - Equal arrival time surface (EATS) integration to account for
    photon arrival time differences across the spherical blast wave.
  - Self-absorption, cooling, and minimum electron energy breaks.

Usage:
  - Edit the physical parameters at the top of this file.
  - Run: python3 grb_afterglow_lc.py
  - Output: two-column print (time[days] flux[mJy]) and
    afterglow_lightcurve.png plot.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ============================================================
# >>>>>>> User-defined physical parameters (edit these) <<<<<<<<
# ============================================================

z = 1.0                    # redshift
E_iso = 1e53               # isotropic-equivalent energy (erg)
epsilon_e = 0.1            # fraction of post-shock energy in electrons
epsilon_B = 0.01           # fraction of post-shock energy in magnetic field
n_0 = 1.0                  # ISM number density (cm^-3)
p = 2.5                    # electron power-law index (p > 2)
nu_obs = 1e17              # observing frequency (Hz)
t_obs_days = np.logspace(-1, 2, 60)  # observer times (days)

# ============================================================
# Physical constants (cgs units)
# ============================================================
_C = 2.99792458e10            # speed of light  cm/s
_PROTON_MASS = 1.67262192e-24 # g
_ELECTRON_MASS = 9.1093837e-28  # g
_ELEC_CHARGE = 4.8032047e-10  # esu
_THOMSON_CS = 6.6524587e-25   # cm^2
_MPC = 3.08567758e24          # cm / Mpc


def _luminosity_distance(z_val):
    """
    Compute luminosity distance d_L (cm) for a flat Lambda-CDM cosmology.
    H0 = 70 km/s/Mpc, Omega_m = 0.3, Omega_Lambda = 0.7.
    """
    H0_cgs = 70.0 * 1e5 / _MPC
    dh = _C / H0_cgs
    zz = np.linspace(0.0, z_val, 2000)
    E_z = np.sqrt(0.3 * (1.0 + zz) ** 3 + 0.7)
    integral = np.trapezoid(1.0 / E_z, zz)
    return dh * integral * (1.0 + z_val)


def _radius_from_time(t_obs_s, z_val, E_val, n_val):
    """
    Blast-wave radius R (cm) and Lorentz factor Gamma from observer time.

    Uses the Blandford-McKee adiabatic solution in a constant-density ISM:
      E_iso = (16 pi / 17) Gamma^2 R^3 n0 mp c^2
      dt_obs = (1+z) dR / (2 Gamma^2 c)
    =>
      R(t_obs) = [ 17 E_iso t_obs / (2 pi n0 mp c (1+z)) ]^(1/4)
      Gamma(t_obs) = sqrt( 17 E_iso / (16 pi n0 mp c^2 R^3) )
    """
    denom = 2.0 * np.pi * n_val * _PROTON_MASS * _C * (1.0 + z_val)
    R = (17.0 * E_val * t_obs_s / denom) ** 0.25
    Gamma = np.sqrt(17.0 * E_val /
                    (16.0 * np.pi * n_val * _PROTON_MASS * _C ** 2 * R ** 3))
    return R, Gamma


def _magnetic_field(Gamma, eps_B, n_val):
    """Comoving magnetic field (Gauss): B' = sqrt(32 pi eps_B n0 mp c^2) * Gamma."""
    return np.sqrt(32.0 * np.pi * eps_B * n_val * _PROTON_MASS * _C ** 2) * Gamma


def _gamma_m(Gamma, eps_e, p_val):
    """Minimum electron Lorentz factor: gamma_m = eps_e*(p-2)/(p-1)*(mp/me)*Gamma."""
    return eps_e * (p_val - 2.0) / (p_val - 1.0) * \
        (_PROTON_MASS / _ELECTRON_MASS) * Gamma


def _gamma_c(Gamma, R, eps_B, n_val):
    """
    Cooling Lorentz factor: equates synchrotron cooling time to dynamical time.
    gamma_c = 6 pi m_e c / (sigma_T B'^2 t'_dyn)
    """
    B = _magnetic_field(Gamma, eps_B, n_val)
    t_dyn_prime = R / (Gamma * _C)
    return (6.0 * np.pi * _ELECTRON_MASS * _C) / \
        (_THOMSON_CS * B ** 2 * t_dyn_prime)


def _nu_synch(gamma_e, B, Gamma, z_val):
    """
    Observed synchrotron frequency for an electron of Lorentz factor gamma_e.
    nu = (3 e B / (4 pi m_e c)) * gamma_e^2 * Gamma / (1+z)
    """
    nu_prime = (3.0 * _ELEC_CHARGE * B) / (4.0 * np.pi * _ELECTRON_MASS * _C)
    return nu_prime * gamma_e ** 2 * Gamma / (1.0 + z_val)


def _peak_flux_density(R, Gamma, B, n_val, d_L, z_val):
    """
    Peak flux density F_nu,max (erg/s/cm^2/Hz) of the synchrotron spectrum.

    Derived from N_e = (4pi/3) R^3 n0 swept-up electrons, each with
    peak spectral power P'_nu,max = sqrt(3) e^3 B' / (m_e c^2).
    """
    N_e = (4.0 * np.pi / 3.0) * R ** 3 * n_val
    P_nu_max_prime = (np.sqrt(3.0) * _ELEC_CHARGE ** 3 * B) / \
                     (_ELECTRON_MASS * _C ** 2)
    return (1.0 + z_val) * N_e * P_nu_max_prime * Gamma / (4.0 * np.pi * d_L ** 2)


def _self_absorption_frequency(R, Gamma, B, gamma_m, gamma_c, n_val,
                               p_val, nu_m):
    """
    Compute synchrotron self-absorption frequency nu_a (observer frame).

    For slow cooling (nu_m < nu_c): iterates to find where tau_nu = 1.
    For fast cooling (nu_c < nu_m): uses approximate formula.
    Uses optical depth scaling from synchrotron theory (Rybicki & Lightman).
    """
    fast_cooling = _nu_synch(gamma_c, B, Gamma, 0.0) < nu_m * (1.0 + 0.0)
    # (We use z_val=0 for nu_c comparison since it's observer-frame)
    # Actually use the pre-computed nu_c — let's fix the interface

    # Determine cooling regime from gamma_c vs gamma_m
    if gamma_c < gamma_m:
        # Fast cooling
        c1 = 5.0 * _ELEC_CHARGE * n_val * R / (_THOMSON_CS * B * gamma_c ** 5)
        nu_a = (c1 ** (2.0 / 5.0)) * _nu_synch(gamma_c, B, Gamma, 0.0)
        if nu_a >= _nu_synch(gamma_c, B, Gamma, 0.0):
            nu_a = _nu_synch(gamma_c, B, Gamma, 0.0) * 0.5
        return nu_a
    else:
        # Slow cooling: iterate optical depth condition
        nu_a_guess = nu_m * 0.1

        def _tau_nu(nu):
            tau_at_m = (5.0 * _ELEC_CHARGE * n_val * R /
                        (_THOMSON_CS * B * gamma_m ** 5))
            if nu < nu_m:
                return tau_at_m * (nu / nu_m) ** (-5.0 / 3.0)
            else:
                return tau_at_m * (nu / nu_m) ** (-(p_val + 4.0) / 2.0)

        for _ in range(50):
            tau = _tau_nu(nu_a_guess)
            if abs(tau - 1.0) < 1e-8:
                break
            correction = (tau - 1.0) / max(tau, 1e-30)
            nu_a_guess *= (1.0 - 0.5 * correction)
            nu_a_guess = max(nu_a_guess, 1e3)
        return nu_a_guess


def _synchrotron_flux(nu, nu_a, nu_m, nu_c, F_max, p_val, fast_cooling):
    """
    Synchrotron flux density at frequency nu (erg/s/cm^2/Hz).

    Broken power-law spectrum (Sari, Piran & Narayan 1998):
      Fast cooling (nu_c < nu_m):
        nu < nu_a:            F_nu ~ nu^2
        nu_a < nu < nu_c:     F_nu ~ nu^(1/3)
        nu_c < nu < nu_m:     F_nu ~ nu^(-1/2)
        nu > nu_m:            F_nu ~ nu^(-p/2)
      Slow cooling (nu_m < nu_c):
        nu < nu_a:            F_nu ~ nu^2
        nu_a < nu < nu_m:     F_nu ~ nu^(1/3)
        nu_m < nu < nu_c:     F_nu ~ nu^(-(p-1)/2)
        nu > nu_c:            F_nu ~ nu^(-p/2)
    """
    if fast_cooling:
        if nu < nu_a:
            return F_max * (nu / nu_a) ** 2 * (nu_a / nu_c) ** (1.0 / 3.0)
        elif nu < nu_c:
            return F_max * (nu / nu_c) ** (1.0 / 3.0)
        elif nu < nu_m:
            return F_max * (nu / nu_c) ** (-0.5)
        else:
            return F_max * (nu_m / nu_c) ** (-0.5) * (nu / nu_m) ** (-p_val / 2.0)
    else:
        if nu < nu_a:
            return F_max * (nu / nu_a) ** 2 * (nu_a / nu_m) ** (1.0 / 3.0)
        elif nu < nu_m:
            return F_max * (nu / nu_m) ** (1.0 / 3.0)
        elif nu < nu_c:
            return F_max * (nu / nu_m) ** (-(p_val - 1.0) / 2.0)
        else:
            return (F_max * (nu_c / nu_m) ** (-(p_val - 1.0) / 2.0) *
                    (nu / nu_c) ** (-p_val / 2.0))


# ------------------------------------------------------------------
# Equal Arrival Time Surface (EATS) integration
# ------------------------------------------------------------------
def _eats_flux(t_obs_s, nu_obs_val, z_val, E_val, eps_e, eps_B,
               n_val, p_val, d_L):
    """
    Compute flux density (erg/s/cm^2/Hz) using equal arrival time
    surface integration following Granot & Sari (2002).

    For a spherical blast wave, photons emitted from different angles
    theta relative to the line of sight arrive at the observer
    simultaneously if they satisfy the EATS condition.

    Method:
      1. Compute line-of-sight radius R_L and Lorentz factor Gamma_L.
      2. Parameterize the EATS by angle theta:
         R(theta)/R_L = [1 + (Gamma_L * theta)^2 / 8]^(-1)   (BM ISM, m=3)
         Gamma(theta) = Gamma_L * (R/R_L)^(-3/2)
      3. At each theta, compute local B, gamma_m, gamma_c, and the
         local synchrotron flux.
      4. Integrate over theta with the Doppler factor delta^3 weighting:
         F_nu = (1+z)/(2 d_L^2) * integral{
           sin(theta) * R(theta)^2 * DeltaR' * j'_nu' * delta^3 } dtheta

    Returns flux in erg/s/cm^2/Hz.
    """
    R_L, Gamma_L = _radius_from_time(t_obs_s, z_val, E_val, n_val)
    if Gamma_L < 2.0:
        return 0.0

    Beta_L = np.sqrt(1.0 - 1.0 / Gamma_L ** 2)

    # Angular grid
    theta_max = 3.0 / Gamma_L
    N_theta = 80
    theta_arr = np.linspace(0.0, theta_max, N_theta)
    d_theta = theta_arr[1] - theta_arr[0]

    # Line-of-sight reference values
    B_L = _magnetic_field(Gamma_L, eps_B, n_val)
    gm_L = _gamma_m(Gamma_L, eps_e, p_val)
    gc_L = _gamma_c(Gamma_L, R_L, eps_B, n_val)
    nu_m_L = _nu_synch(gm_L, B_L, Gamma_L, z_val)
    nu_c_L = _nu_synch(gc_L, B_L, Gamma_L, z_val)
    fast_c_L = nu_c_L < nu_m_L

    # LOS flux for normalization reference
    F_max_L = _peak_flux_density(R_L, Gamma_L, B_L, n_val, d_L, z_val)
    nu_a_L = _self_absorption_frequency(R_L, Gamma_L, B_L,
                                        gm_L, gc_L, n_val, p_val, nu_m_L)
    F_LOS = _synchrotron_flux(nu_obs_val, nu_a_L, nu_m_L, nu_c_L,
                               F_max_L, p_val, fast_c_L)

    # Integrate over EATS
    flux_integral = 0.0
    norm_integral = 0.0

    for theta in theta_arr:
        sin_theta = np.sin(theta)
        if sin_theta < 1e-30:
            sin_theta = max(theta, 1e-30)

        # EATS position
        y = (Gamma_L * theta) ** 2
        R_th = R_L / (1.0 + y / 8.0)
        Gamma_th = Gamma_L * (R_th / R_L) ** (-1.5)
        if Gamma_th < 1.5:
            continue
        Beta_th = np.sqrt(1.0 - 1.0 / Gamma_th ** 2)
        cos_theta = np.cos(theta)
        delta = 1.0 / (Gamma_th * (1.0 - Beta_th * cos_theta))

        # Local synchrotron spectrum
        B_th = _magnetic_field(Gamma_th, eps_B, n_val)
        gm_th = _gamma_m(Gamma_th, eps_e, p_val)
        gc_th = _gamma_c(Gamma_th, R_th, eps_B, n_val)
        nu_m_th = _nu_synch(gm_th, B_th, Gamma_th, z_val)
        nu_c_th = _nu_synch(gc_th, B_th, Gamma_th, z_val)
        fast_th = nu_c_th < nu_m_th
        F_max_th = _peak_flux_density(R_th, Gamma_th, B_th,
                                      n_val, d_L, z_val)
        nu_a_th = _self_absorption_frequency(R_th, Gamma_th, B_th,
                                             gm_th, gc_th, n_val, p_val,
                                             nu_m_th)
        local_F = _synchrotron_flux(nu_obs_val, nu_a_th, nu_m_th,
                                    nu_c_th, F_max_th, p_val, fast_th)

        # Volume factor: R^3 / Gamma (from dV' ~ R^2 * R/Gamma ~ R^3/Gamma)
        # times DeltaR' ~ R/(12 Gamma)
        vol_weight = (R_th ** 3 / Gamma_th) * sin_theta * d_theta
        flux_integral += vol_weight * (delta ** 3) * local_F

        # Reference (LOS) contribution for normalization
        delta_0 = 2.0 * Gamma_th / (1.0 + (Gamma_th * theta) ** 2)
        vol_0 = (R_th ** 3 / Gamma_th) * sin_theta * d_theta
        F_ref = F_LOS  # use LOS flux as reference
        norm_integral += vol_0 * (delta_0 ** 3) * F_ref

    if norm_integral > 0 and flux_integral > 0:
        return flux_integral * F_LOS / norm_integral
    return F_LOS


def compute_light_curve(use_eats=False):
    """
    Compute the afterglow light curve.

    Parameters
    ----------
    use_eats : bool
        If True, use equal arrival time surface integration.
        If False, use the line-of-sight (homogeneous shell) approximation.

    Returns
    -------
    t_days : ndarray  – observer times in days
    flux_mJy : ndarray – flux density in mJy
    """
    d_L = _luminosity_distance(z)
    t_obs_sec = t_obs_days * 86400.0
    flux_mJy = np.zeros_like(t_obs_days)

    print("# GRB Afterglow Light Curve")
    print("# Parameters:")
    print(f"#   z          = {z}")
    print(f"#   E_iso      = {E_iso:.1e} erg")
    print(f"#   epsilon_e  = {epsilon_e}")
    print(f"#   epsilon_B  = {epsilon_B}")
    print(f"#   n_0        = {n_0} cm^-3")
    print(f"#   p          = {p}")
    print(f"#   nu_obs     = {nu_obs:.3e} Hz")
    print(f"#   d_L        = {d_L / _MPC:.1f} Mpc")
    print("#")

    if use_eats:
        print("# Using equal arrival time surface integration")
    else:
        print("# Using line-of-sight (homogeneous shell) approximation")

    print("#")
    print("# Observer time (days)   Flux density (mJy)")
    print("# -----------------------------------------")

    for idx, (t_d, t_s) in enumerate(zip(t_obs_days, t_obs_sec)):
        # Compute blast-wave radius and Lorentz factor
        R, Gamma = _radius_from_time(t_s, z, E_iso, n_0)

        if Gamma < 1.5:
            flux_mJy[idx] = 0.0
            print(f"  {t_d:10.4f}              0.000000e+00")
            continue

        # Line-of-sight physical conditions
        B = _magnetic_field(Gamma, epsilon_B, n_0)
        gamma_m_val = _gamma_m(Gamma, epsilon_e, p)
        gamma_c_val = _gamma_c(Gamma, R, epsilon_B, n_0)

        # Characteristic frequencies (observer frame)
        nu_m = _nu_synch(gamma_m_val, B, Gamma, z)
        nu_c = _nu_synch(gamma_c_val, B, Gamma, z)
        fast_cooling = nu_c < nu_m

        # Peak flux density (erg/s/cm^2/Hz)
        F_max = _peak_flux_density(R, Gamma, B, n_0, d_L, z)

        # Self-absorption frequency
        nu_a = _self_absorption_frequency(R, Gamma, B,
                                          gamma_m_val, gamma_c_val,
                                          n_0, p, nu_m)

        if use_eats:
            # Full EATS integration
            flux_cgs = _eats_flux(t_s, nu_obs, z, E_iso,
                                  epsilon_e, epsilon_B, n_0, p, d_L)
        else:
            # Homogeneous shell (LOS) approximation
            flux_cgs = _synchrotron_flux(nu_obs, nu_a, nu_m, nu_c,
                                         F_max, p, fast_cooling)

        # Convert erg/s/cm^2/Hz -> mJy
        flux_mJy[idx] = flux_cgs / 1e-26
        print(f"  {t_d:10.4f}              {flux_mJy[idx]:.6e}")

    return t_obs_days, flux_mJy


def plot_light_curve(t_days, flux_mJy):
    """Generate and save the light curve plot."""
    fig, ax = plt.subplots(figsize=(8, 5))

    mask = flux_mJy > 1e-30
    t_plot = t_days[mask]
    f_plot = flux_mJy[mask]

    ax.loglog(t_plot, f_plot, "b-", linewidth=1.5, label="Afterglow")
    ax.set_xlabel("Observer time (days)", fontsize=12)
    ax.set_ylabel("Flux density (mJy)", fontsize=12)
    ax.set_title(
        "GRB Afterglow Light Curve\n"
        fr"$z$={z}, $E_{{\mathrm{{iso}}}}$={E_iso:.0e} erg, "
        fr"$\epsilon_e$={epsilon_e}, $\epsilon_B$={epsilon_B}, "
        fr"$n_0$={n_0} cm$^{{-3}}$, $p$={p}",
        fontsize=11,
    )
    ax.grid(True, alpha=0.3, which="both")
    ax.legend(fontsize=10)

    # Annotate the spectral regime
    R0, G0 = _radius_from_time(t_obs_days[10] * 86400.0, z, E_iso, n_0)
    B0 = _magnetic_field(G0, epsilon_B, n_0)
    gm0 = _gamma_m(G0, epsilon_e, p)
    gc0 = _gamma_c(G0, R0, epsilon_B, n_0)
    nu_m0 = _nu_synch(gm0, B0, G0, z)
    nu_c0 = _nu_synch(gc0, B0, G0, z)
    regime_str = (
        fr"$\nu_m$={nu_m0:.1e} Hz, $\nu_c$={nu_c0:.1e} Hz"
    )
    ax.text(0.05, 0.05, regime_str, transform=ax.transAxes,
            fontsize=9, verticalalignment="bottom",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    plt.savefig("afterglow_lightcurve.png", dpi=150)
    plt.close()
    print("#")
    print("# Plot saved to afterglow_lightcurve.png")


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    t_days, flux_mJy = compute_light_curve(use_eats=False)
    plot_light_curve(t_days, flux_mJy)
