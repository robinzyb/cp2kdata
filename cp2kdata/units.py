# internal units and constant used in cp2k.


c = 2.99792458000000E+08  # Speed of light in vacuum [m/s]
h = 6.62606896000000E-34  # Planck constant (h) [J*s]
hbar = 1.05457162825177E-34  # Planck constant (h-bar) [J*s]
NAvo = 6.02214179000000E+23  # Avogadro constant [1/mol]
kB_J_per_K = 1.38065040000000E-23  # Boltzmann constant [J/K]


# Unit Conversion

au2A = 5.29177208590000E-01
au2s = 2.41888432650478E-17
au2fs = 2.41888432650478E-02
au2J = 4.35974393937059E-18
au2N = 8.23872205491840E-08
au2K = 3.15774647902944E+05
au2KJpermol = 2.62549961709828E+03
au2kcalpermol = 6.27509468713739E+02
au2Pa = 2.94210107994716E+13
au2bar = 2.94210107994716E+08
au2atm = 2.90362800883016E+08
au2eV = 2.72113838565563E+01
au2Hz = 6.57968392072181E+15
au2percm = 2.19474631370540E+05

kB = kB_J_per_K * au2eV / au2J
WaveNumber2eV = au2eV / au2percm
