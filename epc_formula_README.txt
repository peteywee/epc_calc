EPC / Profit Model (Category-Agnostic)
======================================

Formulas (decimals, not %)
--------------------------
O      = Σ_i (w_i * c_i)
E_prod = Σ_i (w_i * c_i * a_i * r_i)
E_bty  = Σ_j (β_j * P_j)
E_bon  = O * Σ_k (q_k * v_k)
E      = E_prod + E_bty + E_bon

Where:
- w_i: share of product clicks to module i (Σ w_i = 1)
- c_i: conversion per click for module i
- a_i: average order value for module i (USD)
- r_i: commission rate for module i (decimal)
- β_j: attach rate per click for bounty j
- P_j: payout per bounty j (USD)
- q_k: share of orders that qualify for bonus k
- v_k: payout per qualifying order (USD)

How to Run
----------
1) Edit model_example.json to your real numbers.
2) Run:
   python3 epc_model.py --in /mnt/data/model_example.json --out /mnt/data/epc_result.json --margin 0.30

Outputs
-------
- EPC (USD/click)
- Revenue per 1000 clicks (USD)
- Orders per 1000 clicks
- Break-even CPC, CPC cap for a target margin
- Component breakdowns (products, bounties, bonuses)

Notes
-----
- All rates are decimals (e.g., 3% -> 0.03).
- Module weights must sum to 1.
- Use as few or as many modules, bounties, and bonuses as needed.
