# Pred-Arbitrage
Capturing Arbitrages between Polymarket &amp; Limitless across hourly crypto markets , which is scalable to all markets.


A prediction-market trading framework focused on Polymarket, YES/NO market microstructure, execution engines, and arbitrage research.

This repository is designed for serious experimentation with automated and semi-automated trading strategies in binary prediction markets, with a strong emphasis on:

correct bid/ask logic
clean execution separation
modular strategy design
arbitrage detection

 What This Repo Is :
 
A research & execution codebase for prediction markets
A playground for market microstructure–aware strategies
A framework, not a finished bot
Built to scale from experiments → real execution


Modules Explained

🔹 Polymarket.py


Core abstraction layer for Polymarket.

Responsibilities:
Market discovery and parsing
YES / NO price interpretation
Orderbook logic
Strategy-friendly interfaces

This file defines how the system understands a market.

🔹 Poly_execution

Polymarket-specific execution engine.

Responsibilities:
Order placement
Execution logic
Trade lifecycle handling

Position sizing & safety constraints

This layer answers:
“How do trades actually hit the market?”

🔹 Limitless.py

Experimental strategy sandbox.

Responsibilities:
Rapid idea testing
Aggressive / unconstrained strategies
Alpha exploration without execution risk

Think of this as:
pure strategy logic, zero execution noise

🔹 Limitless_Execution

Execution engine for Limitless.py.

Responsibilities:
Keeps strategy logic isolated
Allows fast iteration
Prevents strategy code from touching execution internals

🔹 Arbitrage

Arbitrage research and construction.

Responsibilities:
Cross-market arbitrage
Intra-market inefficiency detection
Price discrepancy logic
Opportunity filtering

Used for spotting:
mispriced YES/NO pairs
correlated market inefficiencies
execution-safe arbitrage paths

🔹 Markets.json

Single source of truth for markets.

Contains:

-Market IDs
-Outcome definitions
-Metadata used across all strategies
-Consistent references across modules
-Every strategy and execution layer reads from here.
