import numpy as np

from cp2kdata.block_parser.stress import parse_stress_tensor_list


def test_parse_cp2k_2025_stress_in_bar():
    output = """
 STRESS| Analytical stress tensor [GPa]
 STRESS|                        x                     y                     z
 STRESS| x          -1.00000000000E+00   2.00000000000E+00   3.00000000000E+00
 STRESS| y           4.00000000000E+00  -5.00000000000E+00   6.00000000000E+00
 STRESS| z           7.00000000000E+00   8.00000000000E+00  -9.00000000000E+00
 STRESS| Analytical stress tensor [bar]
 STRESS|                        x                     y                     z
 STRESS| x          -1.00000000000E+04   2.00000000000E+04   3.00000000000E+04
 STRESS| y           4.00000000000E+04  -5.00000000000E+04   6.00000000000E+04
 STRESS| z           7.00000000000E+04   8.00000000000E+04  -9.00000000000E+04
"""
    expected = np.array(
        [
            [-1.0, 2.0, 3.0],
            [4.0, -5.0, 6.0],
            [7.0, 8.0, -9.0],
        ]
    )

    stresses = parse_stress_tensor_list(output)

    assert stresses.shape == (2, 3, 3)
    np.testing.assert_allclose(stresses[0], expected)
    np.testing.assert_allclose(stresses[1], expected)
