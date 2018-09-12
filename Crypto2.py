import numpy as np
import xlrd

ALPHABET_DICT: dict = dict(zip([chr(i) for i in range(65, 91)], [i % 26 for i in range(1, 27)]))
NUMERIC_DICT: dict = dict(zip(ALPHABET_DICT.values(), ALPHABET_DICT.keys()))

workbook = xlrd.open_workbook(r'./essential_words_cn.xls')
word_sheet = workbook.sheet_by_index(1)
NORMAL_WORD = list(map(lambda x: x.upper(), word_sheet.col_values(0)))

print(NORMAL_WORD)


def encrypt(dcrypted_str: str, key_matrix: np.matrix):
    if dcrypted_str.__len__() % 2:
        dcrypted_str = dcrypted_str + dcrypted_str[-1]
    ori_m = np.matrix(list(map(lambda x: ALPHABET_DICT[x], dcrypted_str))).reshape(-1, 2)
    enc_m = np.dot(ori_m, key_matrix).reshape(1, -1)
    return ''.join(map(lambda x: NUMERIC_DICT[x % 26], enc_m.tolist()[0]))


def decrypt(ecrypted_str: str, key_matrix: np.matrix) -> str:
    if ecrypted_str.__len__() % 2:
        ecrypted_str = ecrypted_str + ecrypted_str[-1]
    ori_m = np.matrix(list(map(lambda x: ALPHABET_DICT[x], ecrypted_str))).reshape(-1, 2)
    dec_m = np.dot(ori_m, key_matrix.I).reshape(1, -1)
    try:
        return ''.join(map(lambda x: NUMERIC_DICT[round(x % 26) if abs(x - round(x)) < 1e-5 else x], dec_m.tolist()[0]))
    except KeyError:
        return None


def crack(ecrypted_str: str, max_hope: int):
    result = []
    for a in range(0, max_hope):
        for b in range(0, max_hope):
            for c in range(0, max_hope):
                for d in range(0, max_hope):
                    if not abs(a * d - b * c) < 1e-5:
                        key = np.matrix([[a, b], [c, d]])
                        res = decrypt(ecrypted_str, key)
                        if res is not None:
                            result.append([
                                sum(map(lambda x: res.count(x), NORMAL_WORD)),
                                key,
                                res])
    result.sort(key=lambda x: x[0], reverse=True)
    return result


def judge(string: str) -> int:
    current = 0
    while len(string) > 10:
        for w in NORMAL_WORD:
            tmp = string.find(w)
            if tmp == 0:
                string = string[len(w):]
                break
            elif not tmp == -1:
                return current
        current = current + 1
    return current


if __name__ == '__main__':
    TEST_STR: str = "AOBZKNJUYSWCUQCDHSSYHISHVGABZPLIZFSVDMXMABKYNZTCOPYWNWEEQFSHMQBWKWMQPEOGUQUYMSWPPGKUDIOIKGSEQAUMMQFLKLTNXYIFQVCCYZXUEZCDMDDASEKNRWQYSEZYLXXKKXKLLSPEIGEXQAKBAHEJSRNUAOCAWBLWFAEWFAGOFHUTOPQAWCGUKNVGMQBWKWAOVIGJHQKXTMJHIGQYLXYHRUSEOQJHSRCMBIABUMXLLWN"
    TEST_STR = TEST_STR[:20]

    res = crack(TEST_STR, 26)
    print(res, res.__len__())
