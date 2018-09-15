import numpy as np
import xlrd

ALPHABET_DICT: dict = dict(zip([chr(i) for i in range(65, 91)], [i % 26 for i in range(1, 27)]))
NUMERIC_DICT: dict = dict(zip(ALPHABET_DICT.values(), ALPHABET_DICT.keys()))

workbook = xlrd.open_workbook(r'./essential_words_en.xls')
word_sheet = workbook.sheet_by_index(1)
NORMAL_WORD = list(map(lambda x: x.upper(), word_sheet.col_values(0)))
NORMAL_WORD.sort(key=lambda x: len(x), reverse=True)


def gcd(a, b):
    (a, b) = (b, a) if a < b else (a, b)
    while b:
        a, b = b, a % b
    return abs(a)


def inv_m26(m: np.matrix):
    det_m = round(m[0, 0] * m[1, 1] - m[0, 1] * m[1, 0])
    if not gcd(det_m, 26) == 1:
        return None
    for i in range(0, 26):
        if det_m * i % 26 == 1:
            inv_det_m = i
            break
    return np.mod(inv_det_m * det_m * m.I, 26)


def encrypt(dcrypted_str: str, key_matrix: np.matrix):
    if dcrypted_str.__len__() % 2:
        dcrypted_str = dcrypted_str + dcrypted_str[-1]
    ori_m = np.matrix(list(map(lambda x: ALPHABET_DICT[x], dcrypted_str))).reshape(-1, 2).T
    enc_m = np.dot(key_matrix, ori_m).T.reshape(1, -1)
    return ''.join(map(lambda x: NUMERIC_DICT[x % 26], enc_m.tolist()[0]))


def decrypt(ecrypted_str: str, key_matrix: np.matrix) -> str:
    if ecrypted_str.__len__() % 2:
        ecrypted_str = ecrypted_str + ecrypted_str[-1]
    ori_m = np.matrix(list(map(lambda x: ALPHABET_DICT[x], ecrypted_str))).reshape(-1, 2).T
    dec_m = np.dot(inv_m26(key_matrix), ori_m).T.reshape(1, -1)
    return ''.join(map(lambda x: NUMERIC_DICT[round(x) % 26], dec_m.tolist()[0]))


def crack(ecrypted_str: str, max_hope: int):
    result = []
    for a in range(0, max_hope):
        for b in range(0, max_hope):
            for c in range(0, max_hope):
                for d in range(0, max_hope):
                    key = np.matrix([[a, b], [c, d]])
                    if inv_m26(key) is None:
                        continue
                    res = decrypt(ecrypted_str, key)
                    if res is not None:
                        result.append([
                            sum(map(lambda x: res.count(x), NORMAL_WORD)),
                            # judge(res),
                            key,
                            res])
    result.sort(key=lambda x: x[0], reverse=True)
    return result


def judge(string: str) -> int:
    current = 0
    while len(string) > 0:
        flag = True
        for w in NORMAL_WORD:
            tmp = string.find(w)
            if tmp == 0:
                string = string[len(w):]
                current = current + 1
                flag = False
                break
        if flag:
            return current
    return current


def long_near(pair1, pair2):
    if pair1[1] < pair2[1]:
        return pair1
    elif pair1[1] == pair2[1]:
        return max(pair1, pair2, key=lambda x: len(x[0]))
    else:
        return pair2


def split_text(string):
    final_list = []
    while len(string) > 0:
        current = ['', 10000]
        flag = True
        for w in NORMAL_WORD:
            pos = string.find(w)
            if not pos == -1:
                flag = False
                current = long_near(current, [w, pos])
        if current[1] == 0:
            string = string[len(current[0]):]
            final_list.append(current[0])
        else:
            final_list.append(string[:current[1]])
            string = string[current[1]:]
    return " ".join(final_list)


if __name__ == '__main__':
    TEST_STR: str = "AOBZKNJUYSWCUQCDHSSYHISHVGABZPLIZFSVDMXMABKYNZTCOPYWNWEEQFSHMQBWKWMQPEOGUQUYMSWPPGKUDIOIKGSEQAUMMQFLKLTNXYIFQVCCYZXUEZCDMDDASEKNRWQYSEZYLXXKKXKLLSPEIGEXQAKBAHEJSRNUAOCAWBLWFAEWFAGOFHUTOPQAWCGUKNVGMQBWKWAOVIGJHQKXTMJHIGQYLXYHRUSEOQJHSRCMBIABUMXLLWN"

    MY_STR = "SHUXUEHAONAN"
    MY_KEY = np.matrix([[11, 3], [8, 7]])
    res = decrypt(TEST_STR, MY_KEY)
    print(res)
    print(split_text(res))
    # res = crack(TEST_STR, 26)
    # print(list(filter(lambda x: x[0] > 8, res)), res.__len__())
