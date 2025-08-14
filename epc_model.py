#!/usr/bin/env python3
"""
EPC (Earnings Per Click) calculator — category-agnostic.

Variables (decimals, not %):
- Modules i=1..N:
  w_i (weight; Σw=1), c_i (conv per click), a_i (AOV USD), r_i (commission)
- Bounties j=1..J:
  beta_j (attach per click), P_j (payout USD)
- Bonuses k=1..K:
  q_k (share of ORDERS that qualify), v_k (payout USD)

Core:
O      = sum_i (w_i * c_i)
E_prod = sum_i (w_i * c_i * a_i * r_i)
E_bty  = sum_j (beta_j * P_j)
E_bon  = O * sum_k (q_k * v_k)
E      = E_prod + E_bty + E_bon
"""
import json, argparse, sys
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Module:
    name: str
    weight: float
    conv: float
    aov: float
    rate: float

@dataclass
class Bounty:
    name: str
    attach: float
    payout: float

@dataclass
class Bonus:
    name: str
    order_share: float
    payout: float

def _nonneg(name: str, *vals: float):
    if any(v < 0 for v in vals):
        raise ValueError(f"Negative value in {name}: {vals}")

def compute(model: Dict[str, Any], margin: float = 0.30, strict: bool = False) -> Dict[str, Any]:
    modules = [Module(**m) for m in model.get("modules", [])]
    bounties = [Bounty(**b) for b in model.get("bounties", [])]
    bonuses = [Bonus(**k) for k in model.get("bonuses", [])]

    if strict and not modules:
        raise ValueError("strict mode: at least one module required")

    total_weight = sum(m.weight for m in modules)
    if modules and not (abs(total_weight - 1.0) < 1e-6):
        raise ValueError(f"Module weights must sum to 1.0 (got {total_weight:.6f}).")
    for m in modules:
        _nonneg(f"module '{m.name}'", m.weight, m.conv, m.aov, m.rate)
    for b in bounties:
        _nonneg(f"bounty '{b.name}'", b.attach, b.payout)
    for k in bonuses:
        _nonneg(f"bonus '{k.name}'", k.order_share, k.payout)

    O = sum(m.weight * m.conv for m in modules) if modules else 0.0
    E_prod = sum(m.weight * m.conv * m.aov * m.rate for m in modules) if modules else 0.0
    E_bty  = sum(b.attach * b.payout for b in bounties) if bounties else 0.0
    E_bon  = O * sum(k.order_share * k.payout for k in bonuses) if bonuses else 0.0
    E = E_prod + E_bty + E_bon

    return {
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", required=True, help="Path to model JSON")
    ap.add_argument("--margin", type=float, default=0.30, help="Target margin for CPC cap (default 0.30)")
    ap.add_argument("--out", dest="out_path", default="epc_result.json", help="Where to write result JSON")
    ap.add_argument("--strict", action="store_true", help="Stricter validations (requires modules, weights sum==1)")
    args = ap.parse_args()

    with open(args.in_path, "r") as f:
        model = json.load(f)

    res = compute(model, margin=args.margin, strict=bool(args.strict))
    with open(args.out_path, "w") as f:
        json.dump(res, f, indent=2)

    t, c, p = res["totals"], res["components"], res["pricing"]
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
    try:
        main()
    except Exception as e:
        print(f"[EPC ERROR] {e}", file=sys.stderr)
        sys.exit(1)
