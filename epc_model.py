#!/usr/bin/env python3
"""
EPC (Earnings Per Click) calculator — category-agnostic.

Formula (all decimals, not %):

Let modules i=1..N represent product placements/blocks.
- w_i: share of product clicks going to module i (sum_i w_i = 1)
- c_i: purchase conversion per click for module i
- a_i: average order value for module i (USD)
- r_i: commission rate for module i (decimal, e.g., 0.03)

Let bounties j=1..J represent fixed-payout actions.
- beta_j: attach rate per click for bounty j
- P_j: payout per bounty j (USD)

Let bonuses k=1..K represent per-order adders (e.g., first-purchase bonus).
- q_k: share of ORDERS that qualify for bonus k
- v_k: payout per qualifying order (USD)

Core:
O = sum_i w_i * c_i                                  # orders per click
E_prod = sum_i (w_i * c_i * a_i * r_i)               # EPC from products
E_bty  = sum_j (beta_j * P_j)                         # EPC from bounties
E_bon  = O * sum_k (q_k * v_k)                        # EPC from order-qualified bonuses
E      = E_prod + E_bty + E_bon                       # blended EPC

Outputs:
- E (USD/click), revenue per 1,000 clicks, orders/1,000 clicks
- Break-even CPC = E, CPC cap for margin m (optional)
- Component breakdown
"""

import json, argparse, sys
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Module:
    name: str
    weight: float    # w_i
    conv: float      # c_i
    aov: float       # a_i USD
    rate: float      # r_i (decimal)

@dataclass
class Bounty:
    name: str
    attach: float    # beta_j
    payout: float    # P_j USD

@dataclass
class Bonus:
    name: str
    order_share: float  # q_k
    payout: float       # v_k USD

def compute(model: Dict[str, Any], margin: float = 0.3) -> Dict[str, Any]:
    modules = [Module(**m) for m in model.get("modules", [])]
    bounties = [Bounty(**b) for b in model.get("bounties", [])]
    bonuses = [Bonus(**k) for k in model.get("bonuses", [])]

    # Validations
    total_weight = sum(m.weight for m in modules)
    if modules and not (abs(total_weight - 1.0) < 1e-6):
        raise ValueError(f"Module weights must sum to 1.0 (got {total_weight:.6f}).")
    for m in modules:
        if any(x < 0 for x in [m.weight, m.conv, m.aov, m.rate]):
            raise ValueError(f"Negative value in module '{m.name}'.")
    for b in bounties:
        if any(x < 0 for x in [b.attach, b.payout]):
            raise ValueError(f"Negative value in bounty '{b.name}'.")
    for k in bonuses:
        if any(x < 0 for x in [k.order_share, k.payout]):
            raise ValueError(f"Negative value in bonus '{k.name}'.")

    O = sum(m.weight * m.conv for m in modules) if modules else 0.0
    E_prod = sum(m.weight * m.conv * m.aov * m.rate for m in modules) if modules else 0.0
    E_bty  = sum(b.attach * b.payout for b in bounties) if bounties else 0.0
    E_bon  = O * sum(k.order_share * k.payout for k in bonuses) if bonuses else 0.0
    E = E_prod + E_bty + E_bon

    result = {
        "inputs": model,
        "components": {
            "orders_per_click": O,
            "epc_products": E_prod,
            "epc_bounties": E_bty,
            "epc_bonuses": E_bon
        },
        "totals": {
            "epc": E,
            "revenue_per_1000_clicks": E * 1000.0,
            "orders_per_1000_clicks": O * 1000.0
        },
        "pricing": {
            "breakeven_cpc": E,
            "cpc_cap_for_margin": E * (1.0 - margin),
            "target_margin": margin
        }
    }
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", required=True, help="Path to model JSON input")
    ap.add_argument("--margin", type=float, default=0.3, help="Target margin for CPC cap (default 0.30)")
    ap.add_argument("--out", dest="out_path", default="epc_result.json", help="Where to write result JSON")
    args = ap.parse_args()

    with open(args.in_path, "r") as f:
        model = json.load(f)

    res = compute(model, margin=args.margin)
    with open(args.out_path, "w") as f:
        json.dump(res, f, indent=2)

    # Also print a concise summary
    t = res["totals"]
    c = res["components"]
    p = res["pricing"]
    print("== EPC CALC RESULT ==")
    print(f"EPC (USD/click):         {t['epc']:.6f}")
    print(f"Revenue per 1000 clicks: ${t['revenue_per_1000_clicks']:.2f}")
    print(f"Orders per 1000 clicks:   {t['orders_per_1000_clicks']:.2f}")
    print("--- Components ---")
    print(f"EPC - Products:          {c['epc_products']:.6f}")
    print(f"EPC - Bounties:          {c['epc_bounties']:.6f}")
    print(f"EPC - Bonuses:           {c['epc_bonuses']:.6f}")
    print("--- Pricing Guidance ---")
    print(f"Break-even CPC:          ${p['breakeven_cpc']:.4f}")
    print(f"CPC cap @ margin {p['target_margin']:.0%}: ${p['cpc_cap_for_margin']:.4f}")

if __name__ == "__main__":
    main()
