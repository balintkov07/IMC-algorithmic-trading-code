# IMC-algorithmic-trading-code

# IMC Prosperity 2 – Algorithmic Trading Strategies

This repository contains our team's algorithmic trading code for **IMC Prosperity 2**, a global trading competition organized by [IMC Trading](https://prosperity.imc.com/). In Prosperity 2 (2024), thousands of teams traded virtual products – such as AMETHYSTS, STARFRUIT, ORCHIDS, CHOCOLATE, STRAWBERRIES, ROSES, GIFT_BASKETS and more – on a simulated island exchange, with the goal of maximizing *SeaShells*, the in-game currency. Each round introduced new products and mechanics, and our trading algorithms were evaluated against bots and other teams in a separate simulation environment. :contentReference[oaicite:0]{index=0}

## Project overview

Our code focuses on building **Python-based trading agents** (`Trader` classes) that read the current `TradingState` and output a set of orders per product. We explored several styles of strategies:

- **Round 1 – Market making & signal-based trading**  
  VWAP / moving-average based fair value estimates and simple market-making for AMETHYSTS and STARFRUIT.

- **Round 2 – ORCHIDS & cross-market logic**  
  Trading ORCHIDS while considering external market prices, capacity constraints and (mostly-noisy) environmental signals such as sunlight and humidity.

- **Round 3 – Gift basket & components**  
  ETF-style trading between the GIFT_BASKET and its components (CHOCOLATE, STRAWBERRIES, ROSES), using basket fair value calculations and residuals to drive trades.

## Repository structure

Roughly in order of importance:

- **Core submission traders**
  - `main.py` – integrated multi-product `Trader` implementation used in later rounds.
  - `orchids_round2.py` – Round-2 orchids trader with cross-market logic and EMA-style signals.
  - `Round_3_submission.py` – Round-3 multi-product trader for the chocolate / strawberries / roses / gift basket round.

- **Strategy components & variants**
  - `Vwap.py`, `VWAP_S_and_MM_A.py`, `EMA.py`, `Without_EMA.py` – VWAP and moving-average utilities and strategies for early products.
  - `BASKET_TEST_BAZ.py`, `basket_elements_ALE.py`, `roses_ALE.py`, `Roses_choclate_straw.py` – gift basket and component-leg logic for later rounds.
  - `Market_making_experimental.py`, `Orchids.py` – additional experimental strategies and multi-product traders.

- **Training, backtesting & legacy code**
  - `Training.py`, `Training VWAP both.py`, `Training BazBazAnt.py`, `Training_Ant.py`, `Training experimental.py` – local training / backtesting scripts.
  - `Manual trading 2.py` – manual or semi-manual trading / debugging.
  - Files with `"(copy)"` or very experimental names – older iterations and backups kept for reference.

## How to use

The competition environment expects a `Trader` class with a `run` method. To adapt this code for your own experiments:

1. Use one of the core files (e.g. `main.py` or `Round_3_submission.py`) as a template.
2. Implement or modify the `Trader.run` method to express your own strategy.
3. Plug it into the official Prosperity 2 backtesting / submission environment as described in the competition docs.
