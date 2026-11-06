"""Cox-Ross-Rubinstein binomial tree for European and American options.

price(S, K, T, sigma, r=0.0, q=0.0, steps=500, call=True, american=False)
Rates and the dividend yield q are continuously compounded. Standard library only.
"""
from math import exp, sqrt


def price(S, K, T, sigma, r=0.0, q=0.0, steps=500, call=True, american=False):
    dt = T / steps
    u = exp(sigma * sqrt(dt))
    d = 1 / u
    p = (exp((r - q) * dt) - d) / (u - d)
    if not 0 < p < 1:
        raise ValueError("too few steps for these inputs: the risk-neutral probability is outside (0, 1)")
    disc = exp(-r * dt)
    sign = 1 if call else -1
    # Payoffs at expiry, node j has j up moves.
    values = [max(sign * (S * u ** j * d ** (steps - j) - K), 0.0) for j in range(steps + 1)]
    for n in range(steps - 1, -1, -1):
        for j in range(n + 1):
            cont = disc * (p * values[j + 1] + (1 - p) * values[j])
            if american:
                cont = max(cont, sign * (S * u ** j * d ** (n - j) - K))
            values[j] = cont
    return values[0]


def early_exercise_premium(S, K, T, sigma, r=0.0, q=0.0, steps=500, call=False):
    """What the right to exercise early is worth: American minus European on the same tree."""
    a = price(S, K, T, sigma, r, q, steps, call, american=True)
    e = price(S, K, T, sigma, r, q, steps, call, american=False)
    return a - e
