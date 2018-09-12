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
    for a in range(-max_hope, max_hope):
        for b in range(-max_hope, max_hope):
            for c in range(-max_hope, max_hope):
                for d in range(-max_hope, max_hope):
                    if not abs(a * d - b * c) < 1e-5:
                        key = np.matrix([[a, b], [c, d]])
                        res = decrypt(ecrypted_str, key)
                        if res is not None:
                            if sum(map(lambda w: res.count(w), NORMAL_WORD)) > 10:
                                result.append((key, res.lower()))

    return result

def judge(string: str) -> bool:
    current = 0
    pos = min(map(lambda x: string.find(x), NORMAL_WORD))
    if pos > 6:
        return current
    split_str = string[:]

if __name__ == '__main__':

    TEST_STR: str = "AOBZKNJUYSWCUQCDHSSYHISHVGABZPLIZFSVDMXMABKYNZTCOPYWNWEEQFSHMQBWKWMQPEOGUQUYMSWPPGKUDIOIKGSEQAUMMQFLKLTNXYIFQVCCYZXUEZCDMDDASEKNRWQYSEZYLXXKKXKLLSPEIGEXQAKBAHEJSRNUAOCAWBLWFAEWFAGOFHUTOPQAWCGUKNVGMQBWKWAOVIGJHQKXTMJHIGQYLXYHRUSEOQJHSRCMBIABUMXLLWN"
    TEST_STR = TEST_STR[:60]
    print(crack(TEST_STR, 20))
