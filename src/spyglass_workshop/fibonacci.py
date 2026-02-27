#!/usr/bin/env python3
"""Fibonacci numbers."""


def user_input() -> str:
    """Prompt the user for a Fibonacci index and return a formatted result.

    Reads one line from standard input, converts it to an integer, and
    returns a human-readable string showing both the *n*\\ th Fibonacci
    number and the full sequence up to that index.

    Returns
    -------
    str
        Message of the form:
        ``"Fibonacci number N is: X.  The full list is:\\n[...]"``

    Raises
    ------
    ValueError
        If the input string cannot be parsed as an integer.
    Exception
        Any other exception raised by :func:`f` or :func:`f_list` is
        re-raised unchanged.

    Notes
    -----
    Intended for interactive use from a terminal.  For programmatic
    access call :func:`f` and :func:`f_list` directly.
    """
    try:
        n = input("Please enter a number: ")
        return (
            f"Fibonacci number {n} is: {f(int(n))}. "
            + f"The full list is:\n{f_list(int(n))}"
        )
    except Exception as e:
        raise e


def f(n: int) -> int:
    """Return the nth Fibonacci number.

    Uses an iterative two-variable swap — constant memory, no recursion.

    Parameters
    ----------
    n : int
        Non-negative position in the Fibonacci sequence.  ``n = 0``
        returns ``0``; ``n = 1`` returns ``1``.

    Returns
    -------
    int
        The *n*\\ th Fibonacci number F(n).

    Raises
    ------
    TypeError
        If *n* is not an integer (the ``range`` call will raise).

    Notes
    -----
    The sequence follows the standard mathematical definition::

        F(0) = 0,  F(1) = 1,  F(n) = F(n-1) + F(n-2)

    Negative *n* is silently treated as ``0`` because ``range(n)`` is
    empty for ``n < 1``.

    Examples
    --------
    >>> [f(i) for i in range(8)]
    [0, 1, 1, 2, 3, 5, 8, 13]
    """
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def f_list(n: int) -> list[int]:
    """Return a list of the first n Fibonacci numbers.

    Parameters
    ----------
    n : int
        Number of terms to return.  ``n = 0`` returns an empty list.

    Returns
    -------
    list[int]
        ``[F(1), F(2), ..., F(n)]`` — the first *n* nonzero Fibonacci
        numbers in ascending order.

    Raises
    ------
    TypeError
        If *n* is not an integer.

    Notes
    -----
    The returned list starts at ``F(1) = 1``, not ``F(0) = 0``, matching
    the common convention for enumerating the Fibonacci sequence.  For
    index-based access use :func:`f`.

    Examples
    --------
    >>> f_list(5)
    [1, 1, 2, 3, 5]
    >>> f_list(0)
    []
    """
    out: list[int] = []
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
        out.append(a)
    return out


if __name__ == "__main__":  # pragma: no cover
    print(user_input())
