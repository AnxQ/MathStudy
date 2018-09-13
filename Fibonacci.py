import numpy as np


def fib_np(n: int):
    """
    使用 Numpy 进行矩阵运算
    速度堪比 Matlab 运算速度
    缺陷是：由于 Numpy 的限制，超过第1476项时将会导致矩阵中出现Inf，无法继续迭代
    Normal E.g.
    >>> fib_np(1000)
    Crash here.
    >>> fib_np(1477)
    :param n: Range from 1 to 1476
    :return: the Fibonacci number
    """
    R = np.ones([2, n])
    T = np.matrix([[1, 1], [0, 1]])
    for i in range(1, n):
        R[:, i] = np.dot(np.flipud(R[:, i - 1]), T)
    return int(R[1, n - 2]) if n > 1 else 1


def fib_recursion(n):
    """
    低效率警告.
    这是一种极其懒散的递归写法，甚至你输入100它都会卡住
    :param n:
    :return:
    """
    return 1 if n <= 2 else fib_recursion(n - 1) + fib_recursion(n - 2)


def fib_tail_recursion(n):
    pass

if __name__ == "__main__":
    print(fib_recursion(100))
