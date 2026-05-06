#!/usr/bin/env python3
"""Calculate luminosity distance for a given cosmological redshift.

Uses a flat Lambda-CDM cosmology with basic cosmological constants.
"""

import sys

# Cosmological constants (Planck 2018, approximate)
H0 = 70.0          # Hubble constant [km/s/Mpc]
OMEGA_M = 0.3      # Matter density parameter
OMEGA_L = 0.7      # Dark energy density parameter
C = 299792.458     # Speed of light [km/s]


def e_z(z: float) -> float:
    """Dimensionless Hubble parameter E(z) for flat Lambda-CDM."""
    return (OMEGA_M * (1.0 + z) ** 3 + OMEGA_L) ** 0.5


def comoving_distance_integrand(z: float) -> float:
    """Integrand for comoving distance: 1 / E(z)."""
    return 1.0 / e_z(z)


def luminosity_distance(z: float, n_steps: int = 1000) -> float:
    """Return luminosity distance D_L(z) in Mpc.

    D_L(z) = (c/H0) * (1+z) * integral_0^z dz'/E(z')

    Uses Simpson's rule for numerical integration.
    """
    if z < 0:
        raise ValueError("Redshift must be non-negative.")
    if z == 0:
        return 0.0

    # Simpson's rule requires an even number of intervals
    if n_steps % 2 != 0:
        n_steps += 1

    dz = z / n_steps
    # Evaluate integrand at all points: f0, f1, f2, ..., fn
    points = [comoving_distance_integrand(i * dz) for i in range(n_steps + 1)]

    # Simpson's rule
    integral = points[0] + points[-1]
    for i in range(1, n_steps):
        integral += (4.0 if i % 2 == 1 else 2.0) * points[i]
    integral *= dz / 3.0

    dh = C / H0  # Hubble distance [Mpc]
    return dh * (1.0 + z) * integral


def main() -> None:
    """Main entry: parse redshift argument and print luminosity distance."""
    if len(sys.argv) != 2:
        print("Usage: python3 lum_dist.py <redshift>", file=sys.stderr)
        sys.exit(1)

    try:
        z = float(sys.argv[1])
    except ValueError:
        print(f"Error: redshift must be a number, got '{sys.argv[1]}'",
              file=sys.stderr)
        sys.exit(1)

    try:
        dl = luminosity_distance(z)
        print(f"D_L(z={z}) = {dl:.2f} Mpc")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
