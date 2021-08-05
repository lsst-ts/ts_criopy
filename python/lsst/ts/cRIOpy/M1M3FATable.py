# This file is part of M1M3 GUI.
#
# Developed for the LSST Telescope and Site Systems.  This product includes
# software developed by the LSST Project (https://www.lsst.org).  See the
# COPYRIGHT file at the top-level directory of this distribution for details of
# code ownership.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

__all__ = ["FATABLE", "actuatorIDToIndex", "nearNeighborIndices"]

FATABLE_INDEX = 0
FATABLE_ID = 1
FATABLE_XPOSITION = 2
FATABLE_YPOSITION = 3
FATABLE_ZPOSITION = 4
FATABLE_TYPE = 5
FATABLE_SUBNET = 6
FATABLE_ADDRESS = 7
FATABLE_ORIENTATION = 8
FATABLE_XINDEX = 9
FATABLE_YINDEX = 10
FATABLE_ZINDEX = 11
FATABLE_SINDEX = 12
FATABLE_NEAR_NEIGHBOUR_INDEX = 13

FATABLE = [
    [
        0,
        101,
        0.776782776,
        0,
        -2.158743,
        "SAA",
        3,
        1,
        "NA",
        None,
        None,
        0,
        None,
        [102, 408, 407, 107, 108],
    ],
    [
        1,
        102,
        1.442567993,
        0,
        -2.158743,
        "DAA",
        1,
        17,
        "+Y",
        None,
        0,
        1,
        0,
        [103, 409, 408, 101, 108, 109],
    ],
    [
        2,
        103,
        2.10837793,
        0,
        -2.158743,
        "DAA",
        4,
        17,
        "+Y",
        None,
        1,
        2,
        1,
        [104, 410, 409, 102, 109, 110],
    ],
    [
        3,
        104,
        2.774187988,
        0,
        -2.158743,
        "DAA",
        2,
        17,
        "+Y",
        None,
        2,
        3,
        2,
        [105, 411, 410, 103, 110, 111],
    ],
    [
        4,
        105,
        3.439998047,
        0,
        -2.158743,
        "DAA",
        3,
        17,
        "+Y",
        None,
        3,
        4,
        3,
        [106, 412, 411, 104, 111, 112],
    ],
    [
        5,
        106,
        3.968012939,
        0,
        -2.158743,
        "SAA",
        2,
        1,
        "NA",
        None,
        None,
        5,
        None,
        [412, 105, 112],
    ],
    [
        6,
        107,
        0.44386499,
        -0.57660498,
        -2.158743,
        "SAA",
        1,
        1,
        "NA",
        None,
        None,
        6,
        None,
        [108, 101, 113, 114],
    ],
    [
        7,
        108,
        1.109675049,
        -0.57660498,
        -2.158743,
        "DAA",
        4,
        18,
        "+Y",
        None,
        4,
        7,
        4,
        [109, 102, 101, 107, 114, 115],
    ],
    [
        8,
        109,
        1.775484985,
        -0.57660498,
        -2.158743,
        "DAA",
        2,
        18,
        "+Y",
        None,
        5,
        8,
        5,
        [110, 103, 102, 108, 115, 116],
    ],
    [
        9,
        110,
        2.441295898,
        -0.57660498,
        -2.158743,
        "DAA",
        3,
        18,
        "+Y",
        None,
        6,
        9,
        6,
        [111, 104, 103, 109, 116, 117],
    ],
    [
        10,
        111,
        3.107080078,
        -0.57660498,
        -2.158743,
        "DAA",
        1,
        18,
        "+Y",
        None,
        7,
        10,
        7,
        [112, 105, 104, 110, 117, 118],
    ],
    [
        11,
        112,
        3.772891113,
        -0.57660498,
        -2.158743,
        "DAA",
        4,
        19,
        "-X",
        0,
        None,
        11,
        8,
        [106, 105, 111, 118, 125, 119],
    ],
    [
        12,
        113,
        0,
        -1.153209961,
        -2.158743,
        "DAA",
        2,
        19,
        "+Y",
        None,
        8,
        12,
        9,
        [114, 107, 207, 214, 220, 120],
    ],
    [
        13,
        114,
        0.776782776,
        -1.153209961,
        -2.158743,
        "DAA",
        3,
        19,
        "+Y",
        None,
        9,
        13,
        10,
        [115, 108, 107, 113, 120, 121],
    ],
    [
        14,
        115,
        1.442567993,
        -1.153209961,
        -2.158743,
        "DAA",
        1,
        19,
        "+Y",
        None,
        10,
        14,
        11,
        [116, 109, 108, 114, 121, 122],
    ],
    [
        15,
        116,
        2.10837793,
        -1.153209961,
        -2.158743,
        "DAA",
        4,
        20,
        "+Y",
        None,
        11,
        15,
        12,
        [117, 110, 109, 115, 122, 123],
    ],
    [
        16,
        117,
        2.774187988,
        -1.153209961,
        -2.158743,
        "DAA",
        2,
        20,
        "+Y",
        None,
        12,
        16,
        13,
        [118, 111, 110, 116, 123, 124],
    ],
    [
        17,
        118,
        3.439998047,
        -1.153209961,
        -2.158743,
        "DAA",
        3,
        20,
        "+Y",
        None,
        13,
        17,
        14,
        [119, 112, 111, 117, 124, 125],
    ],
    [
        18,
        119,
        3.9005,
        -0.997687012,
        -2.158743,
        "SAA",
        2,
        2,
        "NA",
        None,
        None,
        18,
        None,
        [112, 111, 118, 125],
    ],
    [
        19,
        120,
        0.44386499,
        -1.729819946,
        -2.158743,
        "DAA",
        1,
        20,
        "+Y",
        None,
        14,
        19,
        15,
        [121, 114, 113, 220, 126, 127],
    ],
    [
        20,
        121,
        1.109675049,
        -1.729819946,
        -2.158743,
        "DAA",
        4,
        21,
        "+Y",
        None,
        15,
        20,
        16,
        [122, 115, 114, 120, 127, 128],
    ],
    [
        21,
        122,
        1.775484985,
        -1.729819946,
        -2.158743,
        "DAA",
        2,
        21,
        "+Y",
        None,
        16,
        21,
        17,
        [123, 116, 115, 121, 128, 129],
    ],
    [
        22,
        123,
        2.44127002,
        -1.729819946,
        -2.158743,
        "DAA",
        3,
        21,
        "+Y",
        None,
        17,
        22,
        18,
        [124, 117, 116, 122, 129, 130],
    ],
    [
        23,
        124,
        3.107080078,
        -1.729819946,
        -2.158743,
        "DAA",
        1,
        21,
        "+Y",
        None,
        18,
        23,
        19,
        [125, 118, 117, 123, 130, 131],
    ],
    [
        24,
        125,
        3.724452881,
        -1.517949951,
        -2.158743,
        "SAA",
        4,
        1,
        "NA",
        None,
        None,
        24,
        None,
        [119, 118, 124, 131],
    ],
    [
        25,
        126,
        0,
        -2.306419922,
        -2.158743,
        "DAA",
        2,
        22,
        "+Y",
        None,
        19,
        25,
        20,
        [127, 120, 220, 227, 232, 132],
    ],
    [
        26,
        127,
        0.776782776,
        -2.306419922,
        -2.158743,
        "DAA",
        3,
        22,
        "+Y",
        None,
        20,
        26,
        21,
        [128, 121, 120, 126, 132, 133],
    ],
    [
        27,
        128,
        1.442567993,
        -2.306419922,
        -2.158743,
        "DAA",
        1,
        22,
        "-X",
        1,
        None,
        27,
        22,
        [129, 122, 121, 127, 133, 134],
    ],
    [
        28,
        129,
        2.10837793,
        -2.306419922,
        -2.158743,
        "DAA",
        4,
        22,
        "+Y",
        None,
        21,
        28,
        23,
        [130, 123, 122, 128, 134, 135],
    ],
    [
        29,
        130,
        2.774187988,
        -2.306419922,
        -2.158743,
        "DAA",
        2,
        23,
        "+Y",
        None,
        22,
        29,
        24,
        [131, 124, 123, 129, 135, 136],
    ],
    [
        30,
        131,
        3.387954102,
        -2.167409912,
        -2.158743,
        "SAA",
        3,
        2,
        "NA",
        None,
        None,
        30,
        None,
        [125, 124, 130, 136],
    ],
    [
        31,
        132,
        0.44386499,
        -2.883030029,
        -2.158743,
        "DAA",
        1,
        23,
        "+Y",
        None,
        23,
        31,
        25,
        [133, 127, 126, 232, 237, 137, 138],
    ],
    [
        32,
        133,
        1.109675049,
        -2.883030029,
        -2.158743,
        "DAA",
        4,
        23,
        "+Y",
        None,
        24,
        32,
        26,
        [134, 128, 127, 132, 138, 139],
    ],
    [
        33,
        134,
        1.775484985,
        -2.883030029,
        -2.158743,
        "DAA",
        2,
        24,
        "+Y",
        None,
        25,
        33,
        27,
        [135, 129, 128, 133, 139, 140],
    ],
    [
        34,
        135,
        2.44127002,
        -2.883030029,
        -2.158743,
        "DAA",
        3,
        23,
        "-X",
        2,
        None,
        34,
        28,
        [136, 130, 129, 134, 140],
    ],
    [
        35,
        136,
        2.939364014,
        -2.745179932,
        -2.158743,
        "SAA",
        4,
        2,
        "NA",
        None,
        None,
        35,
        None,
        [131, 130, 129, 135],
    ],
    [
        36,
        137,
        0.221945206,
        -3.459629883,
        -2.158743,
        "DAA",
        2,
        25,
        "+Y",
        None,
        26,
        36,
        29,
        [138, 132, 232, 237, 241, 141],
    ],
    [
        37,
        138,
        0.88772998,
        -3.459629883,
        -2.158743,
        "DAA",
        3,
        24,
        "+Y",
        None,
        27,
        37,
        30,
        [139, 133, 132, 137, 141, 142, 143],
    ],
    [
        38,
        139,
        1.553540039,
        -3.267429932,
        -2.158743,
        "SAA",
        1,
        2,
        "NA",
        None,
        None,
        38,
        None,
        [134, 133, 138, 142, 143, 140],
    ],
    [
        39,
        140,
        2.089733887,
        -3.436389893,
        -2.158743,
        "SAA",
        4,
        3,
        "NA",
        None,
        None,
        39,
        None,
        [135, 134, 139, 143],
    ],
    [
        40,
        141,
        0.365734589,
        -4.00525,
        -2.158743,
        "SAA",
        1,
        3,
        "NA",
        None,
        None,
        40,
        None,
        [142, 138, 137, 237, 241],
    ],
    [
        41,
        142,
        1.085088013,
        -3.87276001,
        -2.158743,
        "SAA",
        2,
        3,
        "NA",
        None,
        None,
        41,
        None,
        [143, 139, 138, 141],
    ],
    [
        42,
        143,
        1.60401001,
        -3.692780029,
        -2.158743,
        "SAA",
        3,
        3,
        "NA",
        None,
        None,
        42,
        None,
        [140, 139, 134, 133, 138, 142],
    ],
    [
        43,
        207,
        -0.44386499,
        -0.57660498,
        -2.158743,
        "SAA",
        1,
        4,
        "NA",
        None,
        None,
        43,
        None,
        [107, 301, 208, 214, 113],
    ],
    [
        44,
        208,
        -1.109680054,
        -0.57660498,
        -2.158743,
        "DAA",
        4,
        24,
        "+Y",
        None,
        28,
        44,
        31,
        [207, 301, 302, 209, 215, 214],
    ],
    [
        45,
        209,
        -1.77548999,
        -0.57660498,
        -2.158743,
        "DAA",
        2,
        26,
        "+Y",
        None,
        29,
        45,
        32,
        [208, 302, 303, 210, 216, 215],
    ],
    [
        46,
        210,
        -2.441300049,
        -0.57660498,
        -2.158743,
        "DAA",
        3,
        25,
        "+Y",
        None,
        30,
        46,
        33,
        [209, 303, 304, 211, 217, 216],
    ],
    [
        47,
        211,
        -3.107080078,
        -0.57660498,
        -2.158743,
        "DAA",
        1,
        24,
        "+Y",
        None,
        31,
        47,
        34,
        [210, 304, 305, 212, 219, 218, 217],
    ],
    [
        48,
        212,
        -3.772889893,
        -0.57660498,
        -2.158743,
        "DAA",
        4,
        25,
        "+X",
        3,
        None,
        48,
        35,
        [211, 305, 306, 219, 225, 218],
    ],
    [
        49,
        214,
        -0.77678302,
        -1.153209961,
        -2.158743,
        "DAA",
        3,
        26,
        "+Y",
        None,
        32,
        49,
        36,
        [113, 207, 208, 215, 221, 220],
    ],
    [
        50,
        215,
        -1.442569946,
        -1.153209961,
        -2.158743,
        "DAA",
        1,
        25,
        "+Y",
        None,
        33,
        50,
        37,
        [214, 208, 209, 216, 222, 221],
    ],
    [
        51,
        216,
        -2.108379883,
        -1.153209961,
        -2.158743,
        "DAA",
        4,
        26,
        "+Y",
        None,
        34,
        51,
        38,
        [215, 209, 210, 217, 223, 222],
    ],
    [
        52,
        217,
        -2.774189941,
        -1.153209961,
        -2.158743,
        "DAA",
        2,
        27,
        "+Y",
        None,
        35,
        52,
        39,
        [216, 210, 211, 218, 224, 223],
    ],
    [
        53,
        218,
        -3.44,
        -1.153209961,
        -2.158743,
        "DAA",
        3,
        27,
        "+Y",
        None,
        36,
        53,
        40,
        [217, 211, 212, 219, 225, 224],
    ],
    [
        54,
        219,
        -3.9005,
        -0.997687012,
        -2.158743,
        "SAA",
        2,
        4,
        "NA",
        None,
        None,
        54,
        None,
        [211, 212, 225, 218],
    ],
    [
        55,
        220,
        -0.44386499,
        -1.729819946,
        -2.158743,
        "DAA",
        1,
        26,
        "+Y",
        None,
        37,
        55,
        41,
        [120, 113, 214, 221, 227, 126],
    ],
    [
        56,
        221,
        -1.109680054,
        -1.729819946,
        -2.158743,
        "DAA",
        4,
        27,
        "+Y",
        None,
        38,
        56,
        42,
        [220, 214, 215, 222, 228, 227],
    ],
    [
        57,
        222,
        -1.77548999,
        -1.729819946,
        -2.158743,
        "DAA",
        2,
        28,
        "+Y",
        None,
        39,
        57,
        43,
        [221, 215, 216, 223, 229, 228],
    ],
    [
        58,
        223,
        -2.44127002,
        -1.729819946,
        -2.158743,
        "DAA",
        3,
        28,
        "+Y",
        None,
        40,
        58,
        44,
        [222, 216, 217, 224, 230, 229],
    ],
    [
        59,
        224,
        -3.107080078,
        -1.729819946,
        -2.158743,
        "DAA",
        1,
        27,
        "+Y",
        None,
        41,
        59,
        45,
        [223, 217, 218, 225, 231, 230],
    ],
    [
        60,
        225,
        -3.724449951,
        -1.517949951,
        -2.158743,
        "SAA",
        4,
        4,
        "NA",
        None,
        None,
        60,
        None,
        [218, 219, 231, 224],
    ],
    [
        61,
        227,
        -0.77678302,
        -2.306419922,
        -2.158743,
        "DAA",
        3,
        29,
        "+Y",
        None,
        42,
        61,
        46,
        [126, 220, 221, 228, 233, 232],
    ],
    [
        62,
        228,
        -1.442569946,
        -2.306419922,
        -2.158743,
        "DAA",
        1,
        28,
        "+X",
        4,
        None,
        62,
        47,
        [227, 221, 222, 229, 234, 233],
    ],
    [
        63,
        229,
        -2.108379883,
        -2.306419922,
        -2.158743,
        "DAA",
        4,
        28,
        "+Y",
        None,
        43,
        63,
        48,
        [228, 222, 223, 230, 236, 235, 234],
    ],
    [
        64,
        230,
        -2.774189941,
        -2.306419922,
        -2.158743,
        "DAA",
        2,
        29,
        "+Y",
        None,
        44,
        64,
        49,
        [229, 223, 224, 231, 236, 235],
    ],
    [
        65,
        231,
        -3.387949951,
        -2.167409912,
        -2.158743,
        "SAA",
        3,
        4,
        "NA",
        None,
        None,
        65,
        None,
        [230, 224, 225, 236],
    ],
    [
        66,
        232,
        -0.44386499,
        -2.883030029,
        -2.158743,
        "DAA",
        1,
        29,
        "+Y",
        None,
        45,
        66,
        50,
        [132, 126, 227, 233, 238, 237, 137],
    ],
    [
        67,
        233,
        -1.109680054,
        -2.883030029,
        -2.158743,
        "DAA",
        4,
        29,
        "+Y",
        None,
        46,
        67,
        51,
        [232, 227, 228, 234, 239, 238],
    ],
    [
        68,
        234,
        -1.77548999,
        -2.883030029,
        -2.158743,
        "DAA",
        2,
        30,
        "+Y",
        None,
        47,
        68,
        52,
        [233, 228, 229, 235, 240, 243, 239],
    ],
    [
        69,
        235,
        -2.44127002,
        -2.883030029,
        -2.158743,
        "DAA",
        3,
        30,
        "+X",
        5,
        None,
        69,
        53,
        [234, 229, 230, 236, 240],
    ],
    [
        70,
        236,
        -2.939360107,
        -2.745179932,
        -2.158743,
        "SAA",
        4,
        5,
        "NA",
        None,
        None,
        70,
        None,
        [235, 229, 230, 231],
    ],
    [
        71,
        237,
        -0.221945007,
        -3.459629883,
        -2.158743,
        "DAA",
        2,
        31,
        "+Y",
        None,
        48,
        71,
        54,
        [137, 132, 232, 238, 241, 141],
    ],
    [
        72,
        238,
        -0.88772998,
        -3.459629883,
        -2.158743,
        "DAA",
        3,
        31,
        "+Y",
        None,
        49,
        72,
        55,
        [237, 232, 233, 239, 243, 242, 241],
    ],
    [
        73,
        239,
        -1.553540039,
        -3.267429932,
        -2.158743,
        "SAA",
        1,
        5,
        "NA",
        None,
        None,
        73,
        None,
        [233, 234, 240, 243, 242, 238],
    ],
    [
        74,
        240,
        -2.08972998,
        -3.436389893,
        -2.158743,
        "SAA",
        4,
        6,
        "NA",
        None,
        None,
        74,
        None,
        [239, 234, 235, 243],
    ],
    [
        75,
        241,
        -0.365734985,
        -4.00525,
        -2.158743,
        "SAA",
        1,
        6,
        "NA",
        None,
        None,
        75,
        None,
        [141, 137, 237, 238, 242],
    ],
    [
        76,
        242,
        -1.085089966,
        -3.87276001,
        -2.158743,
        "SAA",
        2,
        5,
        "NA",
        None,
        None,
        76,
        None,
        [241, 238, 239, 243],
    ],
    [
        77,
        243,
        -1.60401001,
        -3.692780029,
        -2.158743,
        "SAA",
        3,
        5,
        "NA",
        None,
        None,
        77,
        None,
        [238, 239, 234, 240, 242],
    ],
    [
        78,
        301,
        -0.77678302,
        0,
        -2.158743,
        "SAA",
        3,
        6,
        "NA",
        None,
        None,
        78,
        None,
        [307, 308, 302, 208, 207],
    ],
    [
        79,
        302,
        -1.442569946,
        0,
        -2.158743,
        "DAA",
        1,
        30,
        "+Y",
        None,
        50,
        79,
        56,
        [301, 308, 309, 303, 209, 208],
    ],
    [
        80,
        303,
        -2.108379883,
        0,
        -2.158743,
        "DAA",
        4,
        30,
        "+Y",
        None,
        51,
        80,
        57,
        [302, 309, 310, 304, 210, 209],
    ],
    [
        81,
        304,
        -2.774189941,
        0,
        -2.158743,
        "DAA",
        2,
        32,
        "+Y",
        None,
        52,
        81,
        58,
        [303, 310, 311, 305, 211, 210],
    ],
    [
        82,
        305,
        -3.44,
        0,
        -2.158743,
        "DAA",
        3,
        32,
        "+Y",
        None,
        53,
        82,
        59,
        [304, 311, 312, 306, 212, 211],
    ],
    [
        83,
        306,
        -3.96801001,
        0,
        -2.158743,
        "SAA",
        2,
        6,
        "NA",
        None,
        None,
        83,
        None,
        [305, 312, 212],
    ],
    [
        84,
        307,
        -0.44386499,
        0.576605408,
        -2.158743,
        "SAA",
        1,
        7,
        "NA",
        None,
        None,
        84,
        None,
        [407, 313, 314, 308, 301],
    ],
    [
        85,
        308,
        -1.109680054,
        0.576605408,
        -2.158743,
        "DAA",
        4,
        31,
        "+Y",
        None,
        54,
        85,
        60,
        [307, 314, 315, 309, 302, 301],
    ],
    [
        86,
        309,
        -1.77548999,
        0.576605408,
        -2.158743,
        "DAA",
        2,
        33,
        "+Y",
        None,
        55,
        86,
        61,
        [308, 315, 316, 310, 303, 302],
    ],
    [
        87,
        310,
        -2.441300049,
        0.576605408,
        -2.158743,
        "DAA",
        3,
        33,
        "+Y",
        None,
        56,
        87,
        62,
        [309, 316, 317, 311, 304, 303],
    ],
    [
        88,
        311,
        -3.107080078,
        0.576605408,
        -2.158743,
        "DAA",
        1,
        31,
        "-Y",
        None,
        57,
        88,
        63,
        [310, 317, 318, 319, 312, 305, 304],
    ],
    [
        89,
        312,
        -3.772889893,
        0.576605408,
        -2.158743,
        "DAA",
        4,
        32,
        "+X",
        6,
        None,
        89,
        64,
        [311, 318, 319, 306, 305, 325],
    ],
    [
        90,
        313,
        0,
        1.15321106,
        -2.158743,
        "DAA",
        2,
        34,
        "+Y",
        None,
        58,
        90,
        65,
        [414, 420, 320, 314, 307, 407],
    ],
    [
        91,
        314,
        -0.77678302,
        1.15321106,
        -2.158743,
        "DAA",
        3,
        34,
        "+Y",
        None,
        59,
        91,
        66,
        [313, 320, 321, 315, 308, 307],
    ],
    [
        92,
        315,
        -1.442569946,
        1.15321106,
        -2.158743,
        "DAA",
        1,
        32,
        "+Y",
        None,
        60,
        92,
        67,
        [314, 321, 322, 316, 309, 308],
    ],
    [
        93,
        316,
        -2.108379883,
        1.15321106,
        -2.158743,
        "DAA",
        4,
        33,
        "+Y",
        None,
        61,
        93,
        68,
        [315, 322, 323, 317, 310, 309],
    ],
    [
        94,
        317,
        -2.774189941,
        1.15321106,
        -2.158743,
        "DAA",
        2,
        35,
        "+Y",
        None,
        62,
        94,
        69,
        [316, 323, 324, 318, 311, 310],
    ],
    [
        95,
        318,
        -3.44,
        1.15321106,
        -2.158743,
        "DAA",
        3,
        35,
        "+Y",
        None,
        63,
        95,
        70,
        [317, 324, 325, 319, 312, 311],
    ],
    [
        96,
        319,
        -3.9005,
        0.997686584,
        -2.158743,
        "SAA",
        2,
        7,
        "NA",
        None,
        None,
        96,
        None,
        [318, 325, 312, 311],
    ],
    [
        97,
        320,
        -0.44386499,
        1.72981604,
        -2.158743,
        "DAA",
        1,
        33,
        "+Y",
        None,
        64,
        97,
        71,
        [420, 326, 327, 321, 314, 313],
    ],
    [
        98,
        321,
        -1.109680054,
        1.72981604,
        -2.158743,
        "DAA",
        4,
        34,
        "+Y",
        None,
        65,
        98,
        72,
        [320, 327, 328, 322, 315, 314],
    ],
    [
        99,
        322,
        -1.77548999,
        1.72981604,
        -2.158743,
        "DAA",
        2,
        36,
        "+Y",
        None,
        66,
        99,
        73,
        [321, 328, 329, 323, 316, 315],
    ],
    [
        100,
        323,
        -2.44127002,
        1.72981604,
        -2.158743,
        "DAA",
        3,
        36,
        "+Y",
        None,
        67,
        100,
        74,
        [322, 329, 330, 324, 317, 316],
    ],
    [
        101,
        324,
        -3.107080078,
        1.72981604,
        -2.158743,
        "DAA",
        1,
        34,
        "+Y",
        None,
        68,
        101,
        75,
        [323, 330, 331, 325, 318, 317],
    ],
    [
        102,
        325,
        -3.724449951,
        1.517954956,
        -2.158743,
        "SAA",
        4,
        7,
        "NA",
        None,
        None,
        102,
        None,
        [324, 331, 319, 318, 312],
    ],
    [
        103,
        326,
        0,
        2.306422119,
        -2.158743,
        "DAA",
        2,
        37,
        "+Y",
        None,
        69,
        103,
        76,
        [427, 432, 332, 327, 320, 420],
    ],
    [
        104,
        327,
        -0.77678302,
        2.306422119,
        -2.158743,
        "DAA",
        3,
        37,
        "+Y",
        None,
        70,
        104,
        77,
        [326, 332, 333, 328, 321, 320],
    ],
    [
        105,
        328,
        -1.442569946,
        2.306422119,
        -2.158743,
        "DAA",
        1,
        35,
        "+X",
        7,
        None,
        105,
        78,
        [327, 333, 334, 329, 322, 321],
    ],
    [
        106,
        329,
        -2.108379883,
        2.306422119,
        -2.158743,
        "DAA",
        4,
        35,
        "+Y",
        None,
        71,
        106,
        79,
        [328, 334, 335, 330, 323, 322],
    ],
    [
        107,
        330,
        -2.774189941,
        2.306422119,
        -2.158743,
        "DAA",
        2,
        38,
        "+Y",
        None,
        72,
        107,
        80,
        [329, 335, 336, 331, 324, 323],
    ],
    [
        108,
        331,
        -3.387949951,
        2.167406982,
        -2.158743,
        "SAA",
        3,
        7,
        "NA",
        None,
        None,
        108,
        None,
        [330, 336, 325, 324],
    ],
    [
        109,
        332,
        -0.44386499,
        2.8830271,
        -2.158743,
        "DAA",
        1,
        36,
        "+Y",
        None,
        73,
        109,
        81,
        [432, 437, 337, 338, 333, 327, 326],
    ],
    [
        110,
        333,
        -1.109680054,
        2.8830271,
        -2.158743,
        "DAA",
        4,
        36,
        "+Y",
        None,
        74,
        110,
        82,
        [332, 338, 339, 334, 328, 327],
    ],
    [
        111,
        334,
        -1.77548999,
        2.8830271,
        -2.158743,
        "DAA",
        2,
        39,
        "-Y",
        None,
        75,
        111,
        83,
        [333, 339, 343, 340, 335, 329, 328],
    ],
    [
        112,
        335,
        -2.44127002,
        2.8830271,
        -2.158743,
        "DAA",
        3,
        38,
        "+X",
        8,
        None,
        112,
        84,
        [334, 340, 336, 330, 329],
    ],
    [
        113,
        336,
        -2.939360107,
        2.745180908,
        -2.158743,
        "SAA",
        4,
        8,
        "NA",
        None,
        None,
        113,
        None,
        [335, 331, 330, 329],
    ],
    [
        114,
        337,
        -0.221945007,
        3.45963208,
        -2.158743,
        "DAA",
        2,
        40,
        "+Y",
        None,
        76,
        114,
        85,
        [437, 441, 341, 342, 338, 332, 432],
    ],
    [
        115,
        338,
        -0.88772998,
        3.45963208,
        -2.158743,
        "DAA",
        3,
        39,
        "+Y",
        None,
        77,
        115,
        86,
        [337, 341, 342, 343, 339, 333, 332],
    ],
    [
        116,
        339,
        -1.553540039,
        3.267430908,
        -2.158743,
        "SAA",
        1,
        8,
        "NA",
        None,
        None,
        116,
        None,
        [338, 342, 343, 340, 335, 334, 333],
    ],
    [
        117,
        340,
        -2.08972998,
        3.436391113,
        -2.158743,
        "SAA",
        4,
        9,
        "NA",
        None,
        None,
        117,
        None,
        [343, 335, 334, 339],
    ],
    [
        118,
        341,
        -0.365734985,
        4.00525,
        -2.158743,
        "SAA",
        1,
        9,
        "NA",
        None,
        None,
        118,
        None,
        [441, 342, 338, 337, 437],
    ],
    [
        119,
        342,
        -1.085089966,
        3.872762939,
        -2.158743,
        "SAA",
        2,
        8,
        "NA",
        None,
        None,
        119,
        None,
        [341, 343, 339, 333, 338, 337],
    ],
    [
        120,
        343,
        -1.60401001,
        3.692779053,
        -2.158743,
        "SAA",
        3,
        8,
        "NA",
        None,
        None,
        120,
        None,
        [342, 340, 339, 334, 333, 338],
    ],
    [
        121,
        407,
        0.44386499,
        0.576605408,
        -2.158743,
        "SAA",
        1,
        10,
        "NA",
        None,
        None,
        121,
        None,
        [408, 414, 313, 307, 101],
    ],
    [
        122,
        408,
        1.109675049,
        0.576605408,
        -2.158743,
        "DAA",
        4,
        37,
        "+Y",
        None,
        78,
        122,
        87,
        [409, 415, 414, 407, 101, 102],
    ],
    [
        123,
        409,
        1.775484985,
        0.576605408,
        -2.158743,
        "DAA",
        2,
        41,
        "+Y",
        None,
        79,
        123,
        88,
        [410, 416, 415, 408, 102, 103],
    ],
    [
        124,
        410,
        2.441295898,
        0.576605408,
        -2.158743,
        "DAA",
        3,
        40,
        "+Y",
        None,
        80,
        124,
        89,
        [411, 417, 416, 409, 103, 104],
    ],
    [
        125,
        411,
        3.107080078,
        0.576605408,
        -2.158743,
        "DAA",
        1,
        37,
        "-Y",
        None,
        81,
        125,
        90,
        [412, 419, 418, 417, 410, 104, 105],
    ],
    [
        126,
        412,
        3.772891113,
        0.576605408,
        -2.158743,
        "DAA",
        4,
        38,
        "-X",
        9,
        None,
        126,
        91,
        [419, 425, 418, 411, 105, 106],
    ],
    [
        127,
        414,
        0.776782776,
        1.15321106,
        -2.158743,
        "DAA",
        3,
        41,
        "+Y",
        None,
        82,
        127,
        92,
        [415, 421, 420, 313, 407, 408],
    ],
    [
        128,
        415,
        1.442567993,
        1.15321106,
        -2.158743,
        "DAA",
        1,
        38,
        "+Y",
        None,
        83,
        128,
        93,
        [416, 422, 421, 414, 408, 409],
    ],
    [
        129,
        416,
        2.10837793,
        1.15321106,
        -2.158743,
        "DAA",
        4,
        39,
        "+Y",
        None,
        84,
        129,
        94,
        [417, 423, 422, 415, 409, 410],
    ],
    [
        130,
        417,
        2.774187988,
        1.15321106,
        -2.158743,
        "DAA",
        2,
        42,
        "+Y",
        None,
        85,
        130,
        95,
        [418, 424, 423, 416, 410, 411],
    ],
    [
        131,
        418,
        3.439998047,
        1.15321106,
        -2.158743,
        "DAA",
        3,
        42,
        "+Y",
        None,
        86,
        131,
        96,
        [419, 425, 424, 417, 411, 412],
    ],
    [
        132,
        419,
        3.9005,
        0.997686584,
        -2.158743,
        "SAA",
        2,
        9,
        "NA",
        None,
        None,
        132,
        None,
        [425, 418, 411, 412],
    ],
    [
        133,
        420,
        0.44386499,
        1.72981604,
        -2.158743,
        "DAA",
        1,
        39,
        "+Y",
        None,
        87,
        133,
        97,
        [421, 427, 326, 320, 313, 414],
    ],
    [
        134,
        421,
        1.109675049,
        1.72981604,
        -2.158743,
        "DAA",
        4,
        40,
        "+Y",
        None,
        88,
        134,
        98,
        [422, 428, 427, 420, 414, 415],
    ],
    [
        135,
        422,
        1.775484985,
        1.72981604,
        -2.158743,
        "DAA",
        2,
        43,
        "+Y",
        None,
        89,
        135,
        99,
        [423, 429, 428, 421, 415, 416],
    ],
    [
        136,
        423,
        2.44127002,
        1.72981604,
        -2.158743,
        "DAA",
        3,
        43,
        "+Y",
        None,
        90,
        136,
        100,
        [424, 430, 429, 422, 416, 417],
    ],
    [
        137,
        424,
        3.107080078,
        1.72981604,
        -2.158743,
        "DAA",
        1,
        40,
        "+Y",
        None,
        91,
        137,
        101,
        [431, 430, 423, 417, 418, 425],
    ],
    [
        138,
        425,
        3.724452881,
        1.517954956,
        -2.158743,
        "SAA",
        4,
        10,
        "NA",
        None,
        None,
        138,
        None,
        [431, 424, 418, 412, 419],
    ],
    [
        139,
        427,
        0.776782776,
        2.306422119,
        -2.158743,
        "DAA",
        3,
        44,
        "+Y",
        None,
        92,
        139,
        102,
        [428, 433, 432, 326, 420, 421],
    ],
    [
        140,
        428,
        1.442567993,
        2.306422119,
        -2.158743,
        "DAA",
        1,
        41,
        "-X",
        10,
        None,
        140,
        103,
        [429, 434, 433, 427, 421, 422],
    ],
    [
        141,
        429,
        2.10837793,
        2.306422119,
        -2.158743,
        "DAA",
        4,
        41,
        "+Y",
        None,
        93,
        141,
        104,
        [430, 436, 435, 434, 428, 422, 423],
    ],
    [
        142,
        430,
        2.774187988,
        2.306422119,
        -2.158743,
        "DAA",
        2,
        44,
        "+Y",
        None,
        94,
        142,
        105,
        [431, 436, 435, 429, 423, 424],
    ],
    [
        143,
        431,
        3.387954102,
        2.167406982,
        -2.158743,
        "SAA",
        3,
        9,
        "NA",
        None,
        None,
        143,
        None,
        [436, 430, 424, 425],
    ],
    [
        144,
        432,
        0.44386499,
        2.8830271,
        -2.158743,
        "DAA",
        1,
        42,
        "+Y",
        None,
        95,
        144,
        106,
        [433, 438, 437, 337, 332, 326, 427],
    ],
    [
        145,
        433,
        1.109675049,
        2.8830271,
        -2.158743,
        "DAA",
        4,
        42,
        "+Y",
        None,
        96,
        145,
        107,
        [434, 439, 438, 432, 427, 428],
    ],
    [
        146,
        434,
        1.775484985,
        2.8830271,
        -2.158743,
        "DAA",
        2,
        45,
        "-Y",
        None,
        97,
        146,
        108,
        [435, 440, 439, 433, 428, 429],
    ],
    [
        147,
        435,
        2.44127002,
        2.8830271,
        -2.158743,
        "DAA",
        3,
        45,
        "-X",
        11,
        None,
        147,
        109,
        [440, 434, 429, 430, 436],
    ],
    [
        148,
        436,
        2.939364014,
        2.745180908,
        -2.158743,
        "SAA",
        4,
        11,
        "NA",
        None,
        None,
        148,
        None,
        [435, 429, 430, 431],
    ],
    [
        149,
        437,
        0.221945206,
        3.45963208,
        -2.158743,
        "DAA",
        2,
        46,
        "+Y",
        None,
        98,
        149,
        110,
        [438, 441, 341, 337, 332, 432],
    ],
    [
        150,
        438,
        0.88772998,
        3.45963208,
        -2.158743,
        "DAA",
        3,
        46,
        "+Y",
        None,
        99,
        150,
        111,
        [439, 443, 442, 441, 437, 432, 433],
    ],
    [
        151,
        439,
        1.553540039,
        3.267430908,
        -2.158743,
        "SAA",
        1,
        11,
        "NA",
        None,
        None,
        151,
        None,
        [440, 443, 442, 438, 433, 434],
    ],
    [
        152,
        440,
        2.089733887,
        3.436391113,
        -2.158743,
        "SAA",
        4,
        12,
        "NA",
        None,
        None,
        152,
        None,
        [443, 439, 434, 435],
    ],
    [
        153,
        441,
        0.365734589,
        4.00525,
        -2.158743,
        "SAA",
        1,
        12,
        "NA",
        None,
        None,
        153,
        None,
        [442, 341, 337, 437, 438],
    ],
    [
        154,
        442,
        1.085088013,
        3.872762939,
        -2.158743,
        "SAA",
        2,
        10,
        "NA",
        None,
        None,
        154,
        None,
        [441, 437, 438, 439, 443],
    ],
    [
        155,
        443,
        1.60401001,
        3.692779053,
        -2.158743,
        "SAA",
        3,
        10,
        "NA",
        None,
        None,
        155,
        None,
        [442, 438, 439, 434, 440],
    ],
]


def actuatorIDToIndex(actuatorId):
    return next(f for f in FATABLE if f[FATABLE_ID] == actuatorId)[FATABLE_INDEX]


def nearNeighborIndices(index):
    return map(actuatorIDToIndex, FATABLE[index][FATABLE_NEAR_NEIGHBOUR_INDEX])
