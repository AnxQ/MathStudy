import numpy as np

ALPHABET_DICT: dict = dict(zip([chr(i) for i in range(65, 91)], [i % 26 for i in range(1, 27)]))
NUMERIC_DICT: dict = dict(zip(ALPHABET_DICT.values(), ALPHABET_DICT.keys()))


def encrypt(dcrypted_str: str, key_matrix: np.matrix) -> str:
    ori_m = np.matrix(list(map(lambda x: ALPHABET_DICT[x], dcrypted_str))).reshape(-1, 3)
    enc_m = np.dot(ori_m, key_matrix).reshape(1, -1)
    return ''.join(map(lambda x: NUMERIC_DICT[x % 26], enc_m.tolist()[0]))


def decrypt(ecrypted_str: str, key_matrix: np.matrix) -> str:
    ori_m = np.matrix(list(map(lambda x: ALPHABET_DICT[x], ecrypted_str))).reshape(-1, 3)
    dec_m = np.dot(ori_m, key_matrix.I).reshape(1, -1)
    return ''.join(map(lambda x: NUMERIC_DICT[x % 26], dec_m.tolist()[0]))


if __name__ == '__main__':
    TEST_STR: str = "THISISGABENEWELLTHANKSFORPLAYINGDOTATWOHAVEFUNANDENJOY"
    TEST_KEY: np.matrix = np.matrix([[1, 0, 0], [1, 1, 2], [0, 1, 1]])
    print(TEST_KEY.I)
    ENCODED_STR = encrypt(TEST_STR, TEST_KEY)
    print(ENCODED_STR)
    print(decrypt(ENCODED_STR, TEST_KEY))
