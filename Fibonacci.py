import numpy as np
from functools import reduce


def fib_np(n: int):
    """
    使用 Numpy 进行矩阵运算
    缺陷是：由于 Numpy 的限制，超过第1476项时将会导致矩阵中出现Inf，无法继续迭代
    Normal E.g.
    >>> fib_np(1000)
    Crash here.
    >>> fib_np(1477)
    :param n: Range from 1 to 1476
    :return: the Fibonacci number
    """
    R = np.ones([2, 1])
    T = np.matrix([[1, 1], [0, 1]])
    for i in range(1, n-1):
        R[:, 0] = np.dot(np.flipud(R[:, 0]), T)
    return int(R[1, 0]) if n > 1 else 1


def fib_np_2(n: int):
    """
    比上面的fib_np更优雅的写法
    :param n:
    :return:
    """
    R = np.ones([2, 1])
    T = np.matrix([[1, 1], [0, 1]])
    return reduce(lambda x, y: np.dot(np.flipud(x), y),
                  [R] + [T for i in range(n - 1)])[1]

def fib_recursion(n: int):
    """
    低效率警告.
    这是一种极其懒散的树状递归，在没有迭代限制的情况下，它会迅速榨干你的系统资源，
    因此甚至你输入100它都会卡住
    :param n:
    :return: the Fibonacci number
    """
    return 1 if n <= 2 else fib_recursion(n - 1) + fib_recursion(n - 2)


def fib_tail_recursion(n: int):
    """
    相比树状递归，尾递归所造成的空间复杂度更小，运算速度相对较快
    :param n:
    :return: the Fibonacci number
    """

    def fib_tail_iter(n, x, y):
        return x if n == 0 else fib_tail_iter(n - 1, y, x + y)

    return fib_tail_iter(n, 0, 1)


def fib_iterate(n: int):
    pass


if __name__ == "__main__":
    print(fib_np(100))
