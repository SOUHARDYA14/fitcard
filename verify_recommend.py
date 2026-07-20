import sqlite3, re, sys, os, json, urllib.request

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "credit_cards.db")

PREF_MAP = {
    "travel":   ["travel", "international", "railways", "trains", "transportation & tolls", "uber"],
    "shopping": ["online", "retail", "departmental stores", "myntra", "flipkart", "grocery", "jewellery"],
    "fuel":     ["fuel"],
    "cashback": ["wallets", "base rewards", "upi"],
    "dining":   ["dining"],
    "movies":   ["movies"],
}

def tier_from_fee(fee):
    if fee is None:   return ("Fee not listed", 1)
    if fee == 0:      return ("Lifetime Free", 1)
    if fee <= 1000:   return ("Entry", 2)
    if fee <= 5000:   return ("Mid-range", 3)
    if fee <= 12500:  return ("Super Premium", 4)
    return ("Luxury", 5)

def ideal_tier(annual_income):
    if annual_income >= 2500000: return 5
    if annual_income >= 1200000: return 4
    if annual_income >= 600000:  return 3
    if annual_income >= 350000:  return 2
    return 1

def min_return(rp):
    if not rp: return 0
    m = re.search(r"(\d+(?:\.\d+)?)", rp)
    return float(m.group(1)) if m else 0

def compute(monthly_income, preference, budget):
    income = monthly_income * 12
    cats = PREF_MAP.get(preference.lower(), [])
    target = ideal_tier(income)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    placeholders = ",".join("?" * len(cats)) if cats else "''"
    rows = conn.execute(f"""
        SELECT c.id, c.card_name, c.bank_name, c.joining_fee, c.return_percentage,
               GROUP_CONCAT(DISTINCT ec.category) AS matched_cats
        FROM credit_cards c
        LEFT JOIN earn_category_groups g ON g.card_id = c.id
        LEFT JOIN earn_categories ec
               ON ec.group_id = g.id
              AND ec.has_rewards = 1
              AND LOWER(ec.category) IN ({placeholders})
        GROUP BY c.id
    """, cats).fetchall()
    conn.close()

    within_budget = []
    excluded_over_budget = 0
    for r in rows:
        fee = r["joining_fee"]
        fee_val = fee if fee is not None else 0
        if fee_val > budget:
            excluded_over_budget += 1
            continue

        tier_name, tier_rank = tier_from_fee(fee)
        score = 0
        detail = []

        if r["matched_cats"]:
            n = len(r["matched_cats"].split(","))
            cat_score = 5 + min(n - 1, 3)
            score += cat_score
            detail.append(f"category:+{cat_score}")

        gap = abs(tier_rank - target)
        if gap == 0:
            score += 3; detail.append("tier_exact:+3")
        elif gap == 1:
            score += 1; detail.append("tier_near:+1")

        ret_score = min_return(r["return_percentage"]) * 0.3
        score += ret_score
        detail.append(f"return:+{round(ret_score,2)}")

        within_budget.append({
            "card_name": r["card_name"],
            "bank_name": r["bank_name"],
            "fee": fee_val,
            "tier": tier_name,
            "return": r["return_percentage"] or "NA",
            "matched": r["matched_cats"] or "",
            "score": round(score, 2),
            "detail": " ".join(detail),
            "shown": score > 0,
        })

    within_budget.sort(key=lambda x: x["score"], reverse=True)
    return within_budget, excluded_over_budget, target

def main():
    monthly_income = int(sys.argv[1]) if len(sys.argv) > 1 else 50000
    preference = sys.argv[2] if len(sys.argv) > 2 else "travel"
    budget = int(sys.argv[3]) if len(sys.argv) > 3 else 5000

    ranked, excluded_over_budget, target = compute(monthly_income, preference, budget)

    print(f"Input: monthly_income={monthly_income} (yearly={monthly_income*12}), "
          f"preference={preference}, budget={budget}")
    print(f"Income tier target: {target}")
    print(f"Cards within budget: {len(ranked)}  |  Excluded for being over budget: {excluded_over_budget}")
    print(f"Cards within budget but score=0 (hidden from results): {sum(1 for c in ranked if not c['shown'])}")
    print()
    print(f"{'#':<3}{'Card':<32}{'Bank':<12}{'Fee':<7}{'Tier':<15}{'Return':<10}{'Score':<7}{'Shown':<7}Breakdown")
    for i, c in enumerate(ranked, 1):
        flag = "  <-- top5" if i <= 5 else ""
        print(f"{i:<3}{c['card_name'][:31]:<32}{c['bank_name'][:11]:<12}{c['fee']:<7}"
              f"{c['tier']:<15}{c['return']:<10}{c['score']:<7}{str(c['shown']):<7}{c['detail']}{flag}")

    print()
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:5000/recommend",
            data=json.dumps({"income": monthly_income, "preference": preference, "budget": budget}).encode(),
            headers={"Content-Type": "application/json"},
        )
        api_result = json.loads(urllib.request.urlopen(req, timeout=5).read())
        api_names = [c["card_name"] for c in api_result]
        expected_names = [c["card_name"] for c in ranked[:5] if c["shown"]]
        print("Live API top 5:     ", api_names)
        print("Recomputed top 5:   ", expected_names)
        print("MATCH" if api_names == expected_names else "MISMATCH")
    except Exception as e:
        print(f"(Could not reach live API at 127.0.0.1:5000: {e})")

if __name__ == "__main__":
    main()
