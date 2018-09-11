from typing import List

normal_frequency = [4, 19, 14, 0, 13, 8, 17, 18, 7, 3, 11, 2, 20, 12, 15, 24, 22, 6, 1, 21, 10, 23, 9, 16, 25]
normal_word = ["and", "is", "in", "at", "of", "by", "the", "not", "can", "are"]
alphabet = [chr(c) for c in range(97, 123)]


def gcd(a, b):
    (a, b) = (b, a) if a < b else (a, b)
    while b != 0:
        temp = a % b
        a = b
        b = temp
    return a


def crack_key(a, b, c, d):
    i = 0
    k = [0, 0]
    while True:
        k[0] = (float(a - d - 26 * i) / float(b - c))
        if k[0] < -26 or k[0] > 26:
            return None
        if int(k[0]) == k[0] and gcd(k[0], 26) == 1:
            k[1] = int(d - c * k[0]) % 26
            k[0] = int(k[0])
            return k
        i = i + 1


def decrypt(ecrpted_str: str, key: List[int]):
    for k in range(0, 26):
        if k * key[0] % 26 == 1:
            key.append(k)
            break
    return ''.join(list(map(lambda c: alphabet[key[2] * (alphabet.index(c) - key[1]) % 26] if c in alphabet else c,
                            ecrpted_str)))


def encrypt(dcrpted_str: str, key: List[int]):

    pass


def crack(ecrpted_str: str):
    prec = 4

    result = []
    origin_frequency = [[alphabet.index(c), ecrpted_str.count(c)] for c in alphabet]
    sorted_frequency = [kw[0] for kw in sorted(origin_frequency, key=lambda x: x[1], reverse=True)]

    for a in sorted_frequency[0:int(len(sorted_frequency) / prec)]:
        for b in normal_frequency[0:int(len(normal_frequency) / prec)]:
            for c in normal_frequency[normal_frequency.index(b) + 1:int(len(normal_frequency) / prec)]:
                for d in sorted_frequency[sorted_frequency.index(a) + 1:int(len(sorted_frequency) / prec)]:
                    key = crack_key(a, b, c, d)
                    if key is not None:
                        predict_str = decrypt(ecrpted_str, key)
                        predict_words = predict_str.split()
                        if predict_words.__len__() < 10:
                            result.append((key, predict_str))
                        elif sum(map(lambda w: w in predict_words, normal_word)) > 4:
                            return (key, predict_str)
    return result


if __name__ == "__main__":
    encrypted_str: str = "lx afhkpsn fsw khd daxwtsad fgt dtts fa akt sp ats vhwwyt dzkppy hs bxsvhsn, " \
                         "zfmhafy pq dpxakrtda zkhsf′d lxssfs mgpuhszt, " \
                         "dtmatvctg dtutsak, arp akpxdfsw fsw dtutsatts. " \
                         "Stutsal−akgtt−ltfg−pyw ltfg lx afhkpsn dafgatw ktg zfgttg fd f atfzktg hs shstatts dhoal−akgtt. " \
                         "fqatg gtahgtvtsa hs rp akpxdfsw, dkt kfd ctts gttvmypltw cl akt sp ats vhwwyt dzkppy xsahy spr. " \
                         "′vl chnntda mytfdxgt hd ap ct rhak vl daxwtsad fsw h rpxyw spa ytfut vl myfaqpgv fd ypsn fd h zfs dafsw xm′ dfhw akt wtupatw atfzktg. " \
                         "akt atfzktgd′ wfl hd ztytcgfatw hs zkhsf ps dtma atsak tutgl ltfg. "
    print(crack(encrypted_str))
