"""Run with: python -m pytest  (or python test_binomial.py)."""
import itertools
from math import erf, exp, log, sqrt

from binomial import early_exercise_premium, price

CASES = list(itertools.product((80.0, 100.0, 120.0), (90.0, 110.0), (0.25, 1.0), (0.15, 0.4), (0.0, 0.06), (0.0, 0.03)))


def N(x):
    return 0.5 * (1 + erf(x / sqrt(2)))


def black_scholes(S, K, T, s, r, q, call=True):
    d1 = (log(S / K) + (r - q + s * s / 2) * T) / (s * sqrt(T))
    d2 = d1 - s * sqrt(T)
    if call:
        return S * exp(-q * T) * N(d1) - K * exp(-r * T) * N(d2)
    return K * exp(-r * T) * N(-d2) - S * exp(-q * T) * N(-d1)


def test_european_matches_black_scholes():
    for S, K, T, s, r, q in CASES:
        for call in (True, False):
            assert abs(price(S, K, T, s, r, q, 800, call) - black_scholes(S, K, T, s, r, q, call)) < 0.02


def test_error_shrinks_with_steps():
    # CRR error oscillates, so compare averages of neighbouring step counts.
    bs = black_scholes(100, 100, 1, 0.2, 0.05, 0)
    coarse = abs((price(100, 100, 1, 0.2, 0.05, steps=50) + price(100, 100, 1, 0.2, 0.05, steps=51)) / 2 - bs)
    fine = abs((price(100, 100, 1, 0.2, 0.05, steps=800) + price(100, 100, 1, 0.2, 0.05, steps=801)) / 2 - bs)
    assert fine < coarse / 5


def test_american_call_without_dividends_is_european():
    for S, K, T, s, r, q in CASES:
        if q == 0:
            assert abs(early_exercise_premium(S, K, T, s, r, 0, 300, call=True)) < 1e-9


def test_american_put_is_worth_more():
    for S, K, T, s, r, q in CASES:
        assert early_exercise_premium(S, K, T, s, r, q, 300, call=False) >= -1e-12
    # With a positive rate the premium on an in-the-money put is strictly positive.
    assert early_exercise_premium(80, 110, 1, 0.2, 0.06, 0, 300) > 0.5


def test_american_put_bounds():
    for S, K, T, s, r, q in CASES:
        a = price(S, K, T, s, r, q, 300, call=False, american=True)
        assert a >= max(K - S, 0) - 1e-12
        assert a <= K + 1e-12


if __name__ == "__main__":
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f()
            print("ok", name)
