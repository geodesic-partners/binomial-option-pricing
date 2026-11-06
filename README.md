# Binomial option pricing in Python, for European and American options

`binomial.py` prices calls and puts on a Cox-Ross-Rubinstein binomial tree using only the standard library. If you pass `american=True`, the tree also tests every node for early exercise, which is the main reason most people bother to write a tree at all. The whole file fits on one screen, so you can read all of it and decide for yourself whether you trust it.

```python
from binomial import price, early_exercise_premium

price(100, 100, 1, 0.2, r=0.05, steps=1000)                            # 10.4486, Black-Scholes says 10.4506
price(100, 100, 1, 0.2, r=0.05, steps=1000, call=False, american=True)  # 6.0896
early_exercise_premium(80, 110, 1, 0.2, r=0.06)                         # 5.57 on a deep in-the-money put
```

Over every time increment the stock moves up by u = exp(sigma * sqrt(dt)) or down by 1/u, and the risk-neutral probability of an up move is p = (exp((r - q) dt) - d) / (u - d). Pricing starts from the payoffs at expiry and works backwards, discounting one level of the tree at a time. For an American option the code keeps whichever is larger, that discounted value or the payoff from exercising on the spot. If you ask for too few steps, p can land outside (0, 1) and you'll get an error, because a tree with negative probabilities can't give a meaningful price.

## What the checks cover

`python -m pytest` (or `python test_binomial.py`) runs five checks over 96 combinations of spot, strike, maturity, volatility, rate and dividend yield:

- at 800 steps, European calls and puts match the closed-form Black-Scholes value to 2 cents
- the error shrinks as you add steps (averaged over neighbouring step counts, since CRR prices zigzag around the true value between odd and even counts)
- with no dividend an American call is worth the same as the European call, as you'd never exercise it early
- an American put is worth at least as much as the European put, and strictly more when the rate is positive and the put is deep in the money
- an American put never falls below its intrinsic value K - S and never rises above K

The third check concerns early exercise, a favourite topic with quant interviewers. Exercising a call early throws away the option's remaining time value and pays the strike sooner than you need to, so with no dividends there's nothing to gain from doing it. Puts work the opposite way round, since receiving K early lets you earn interest on it.

## Speed

The loop is plain Python and the work grows with the square of the step count, so 1,000 steps run in a fraction of a second while 10,000 take a noticeable while. Averaging the prices at n and n + 1 steps gives a quick estimate and cancels most of the odd-even zigzag.

If you're preparing for quant interviews, you'll find worked answers to stochastic calculus and option pricing questions at https://geodesicpartners.co.uk/quant-questions-stochastic-calculus
