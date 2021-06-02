import astropy.units as u

__all__ = ["M2MM", "D2ARCSEC", "MM2M", "ARCSEC2D"]

M2MM = u.m.to(u.mm)
D2ARCSEC = u.deg.to(u.arcsec)

MM2M = 1 / M2MM
ARCSEC2D = 1 / D2ARCSEC
