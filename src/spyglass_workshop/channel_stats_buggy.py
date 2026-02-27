#!/usr/bin/env python3
"""Channel statistics — buggy version for the debugging exercise.

Contains three intentional bugs, each requiring a different debugger
technique.  Fix them in order — each fix reveals the next problem.

Bug 1 — TypeError from a builtin  (fires on every channel immediately)
    ``_mean`` references ``len`` as a value instead of calling
    ``len(values)``.  Python divides by the built-in function object
    rather than by a number, raising ``TypeError`` before any channel
    is processed.  The fix is a single pair of parentheses.

Bug 2 — missing guard clause  (fires after Bug 1 is fixed)
    ``_z_scores`` divides every sample by ``sigma`` without first
    checking whether ``sigma`` is zero.  Because Bug 3 makes
    ``_variance`` return ``0.0`` for every channel, all channels have
    ``sigma == 0`` until that is also fixed.  Inspect ``sigma`` in the
    **Variables** panel to confirm it is ``0.0``, then add an
    early-return guard.

Bug 3 — loop accumulation error  (produces wrong values after Bug 2 is fixed)
    ``_variance`` uses ``sq_devs + [...]`` inside the loop.  The ``+``
    operator creates a new list on each iteration but does not update
    ``sq_devs``, which stays ``[]`` for the entire loop.
    ``sum([]) / n`` is always ``0.0``, so every channel reports
    ``std == 0.0``.  Set a **breakpoint** on the ``sq_devs +`` line,
    step through the loop, and watch ``sq_devs`` in the **Variables**
    panel — it never grows.  Fix with ``sq_devs.append(...)`` or
    ``sq_devs += [...]``.

Run the test suite to verify all three fixes::

    pytest tests/test_channel_stats_buggy.py -v
"""


# NOTE: To hide indented text in VS Code, click the arrows. Or for docstrings:
#       `Ctrl+Shift+P` → "Pylance: Fold All Docstrings"
#       Explore various folding options: "Unfold all", "Fold Level 2", etc.


def dummy_function(
    list_of_list_of_list_of_floats: list[list[list[float]]],
) -> None:
    """This is a dummy function to demonstrate docstring folding."""
    for list_of_list_of_floats in list_of_list_of_list_of_floats:
        for list_of_floats in list_of_list_of_floats:
            for float_value in list_of_floats:
                print(float_value)


def summarize(channels):
    """Return summary statistics for each channel in a multi-channel recording.

    Computes per-channel mean, population standard deviation, and z-scores.
    Channels are processed independently and may have different lengths.

    Parameters
    ----------
    channels : list[list[float]]
        Each inner list is one channel's raw sample values.

    Returns
    -------
    dict[int, dict]
        Mapping from channel index (0-based) to a statistics dict with keys:

        ``"mean"`` : float
            Arithmetic mean of the channel samples.
        ``"std"`` : float
            Population standard deviation (``0.0`` for flat signals).
        ``"z_scores"`` : list[float]
            Z-scored copy of the channel; all ``0.0`` for flat signals.

    Raises
    ------
    ZeroDivisionError
        If any channel is empty (propagated from :func:`_mean`).

    Notes
    -----
    Channels that contain only a single repeated value (e.g. a dead
    electrode) will have ``std == 0`` and ``z_scores`` consisting entirely
    of ``0.0`` once all bugs in this module are fixed.
    """
    return {i: _channel_stats(ch) for i, ch in enumerate(channels)}


def _channel_stats(signal):
    """Compute summary statistics for a single channel.

    Parameters
    ----------
    signal : list[float]
        Raw sample values for one channel.  Must be non-empty.

    Returns
    -------
    dict
        Dict with keys ``"mean"`` (float), ``"std"`` (float), and
        ``"z_scores"`` (list[float]).

    Raises
    ------
    TypeError
        Propagated from :func:`_mean` until Bug 1 is fixed.
    ZeroDivisionError
        Propagated from :func:`_z_scores` until Bug 2 is fixed.
    """
    mu = _mean(signal)
    sigma = _std(signal, mu)
    return {"mean": mu, "std": sigma, "z_scores": _z_scores(signal, mu, sigma)}


def _mean(values):
    """Return the arithmetic mean of *values*.

    Parameters
    ----------
    values : list[float]
        Non-empty sequence of numeric values.

    Returns
    -------
    float
        Arithmetic mean ``sum(values) / len(values)``.

    Raises
    ------
    TypeError
        Bug 1: ``len`` is referenced as a value instead of being called.
        Python raises ``TypeError`` when dividing a number by a function
        object.  Fix: add ``(values)`` to call ``len``.
    ZeroDivisionError
        If *values* is empty (after Bug 1 is fixed).
    """
    # return sum(values) / len
    # Bug 1: should be len(values)
    return sum(values) / len(values)


def _std(values, mu):
    """Return the population standard deviation of *values*.

    Delegates to :func:`_variance` for the accumulation loop and
    :func:`_safe_sqrt` for the square root.

    Parameters
    ----------
    values : list[float]
        Sample values.  Must contain at least one element.
    mu : float
        Pre-computed mean of *values*, as returned by :func:`_mean`.

    Returns
    -------
    float
        Population standard deviation ``sqrt(variance)``.
        Returns ``0.0`` when all values are identical.

    Raises
    ------
    ValueError
        Propagated from :func:`_safe_sqrt` if variance is negative
        (defensive guard against future formula errors).

    Notes
    -----
    Uses the *population* standard deviation (divides by ``n``, not
    ``n - 1``).  Passing a pre-computed *mu* avoids a redundant pass
    over the data.
    """
    variance = _variance(values, mu)
    return _safe_sqrt(variance)


def _variance(values, mu):
    """Return the population variance of *values*.

    Accumulates squared deviations in an explicit ``for`` loop so a
    breakpoint can be set to observe ``sq_devs`` grow on each iteration.

    Parameters
    ----------
    values : list[float]
        Sample values.  Must contain at least one element.
    mu : float
        Pre-computed mean of *values*.

    Returns
    -------
    float
        Population variance ``sum((v - mu)**2) / n``.
        Returns ``0.0`` when all values are identical.

    Notes
    -----
    Bug 3 is on the ``sq_devs +`` line: ``list + [item]`` evaluates to a
    new list but does not modify ``sq_devs``.  Set a **breakpoint** here
    and step through the loop — ``sq_devs`` stays ``[]`` on every pass,
    so ``sum([])`` is always ``0.0``.

    Fix with either of::

        sq_devs.append(_sq_dev(v, mu))  # mutates sq_devs in place
        sq_devs += [_sq_dev(v, mu)]  # augmented assignment rebinds sq_devs
    """
    n = len(values)
    sq_devs = []
    for v in values:
        sq_devs + [_sq_dev(v, mu)]  # Bug 3: new list — sq_devs unchanged
        # print(f"v={v:.2f}, mu={mu:.2f}, sq_dev={_sq_dev(v, mu):.4f}, ")
    return sum(sq_devs) / n


def _sq_dev(v, mu):
    """Return the squared deviation of sample *v* from the mean *mu*.

    Parameters
    ----------
    v : float
        A single sample value.
    mu : float
        Mean of the channel, as returned by :func:`_mean`.

    Returns
    -------
    float
        ``(v - mu) ** 2`` — always non-negative.
    """
    return (v - mu) ** 2


def _safe_sqrt(x):
    """Return the non-negative square root of *x*.

    Raises a descriptive ``ValueError`` when *x* is negative so that any
    future formula error in :func:`_sq_dev` produces a clear diagnostic
    rather than returning ``nan``.

    Parameters
    ----------
    x : float
        A non-negative number (the population variance).

    Returns
    -------
    float
        ``x ** 0.5``.

    Raises
    ------
    ValueError
        If *x* is negative — indicates a bug in the squared-deviation
        formula.
    """
    if x < 0:
        raise ValueError(
            f"variance is negative ({x:.4f}) — check the squared-deviation"
            " formula in _sq_dev"
        )
    return x**0.5


def _z_scores(signal, mu, sigma):
    """Return a z-scored copy of *signal*.

    Each sample is transformed as ``(v - mu) / sigma``.  For constant
    signals where ``sigma == 0``, every z-score is defined as ``0.0``.

    Parameters
    ----------
    signal : list[float]
        Raw sample values.
    mu : float
        Mean of *signal*, as returned by :func:`_mean`.
    sigma : float
        Standard deviation of *signal*, as returned by :func:`_std`.

    Returns
    -------
    list[float]
        Z-scored values, same length as *signal*.

    Raises
    ------
    ZeroDivisionError
        Bug 2: *sigma* is ``0.0`` and no guard clause is present.
        Inspect ``sigma`` in the **Variables** panel, then add::

            if sigma == 0.0:
                return [0.0] * len(signal)

    Notes
    -----
    After correct normalization the z-scores have mean ``0`` and unit
    population standard deviation — provided *mu* and *sigma* are derived
    from the same *signal*.
    """
    # Bug 2: missing guard clause for sigma == 0
    if sigma == 0.0:
        return [0.0] * len(signal)
    return [(v - mu) / sigma for v in signal]


if __name__ == "__main__":  # pragma: no cover
    recording = [
        # normal channel      ← all bugs hit here in turn
        [1.0, 2.0, 3.0, 4.0, 5.0],
        # single-sample burst ← sigma=0 after fixes
        [7.0],
        # dead/flat electrode  ← sigma=0 always (
        [3.0, 3.0, 3.0, 3.0],
    ]
    result = summarize(recording)
    for ch, stats in result.items():
        print(f"Channel {ch}: mean={stats['mean']:.2f}, std={stats['std']:.2f}")
