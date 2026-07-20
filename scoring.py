"""Core recommendation engine: filters credit_cards.db down to eligible cards
for a user's inputs, scores each one, and returns the top 5 with an
explanation for every point awarded.
"""
from collections import defaultdict

from categories import (
    CATEGORY_KEYWORDS, CATEGORY_LABELS,
    parse_effective_rate_percent, parse_return_percentage_midpoint,
)

FEE_CAPS = {"0": 0, "1000": 1000, "5000": 5000, "premium": None}


def tier_label(fee):
    """Rough tier label derived from joining fee, used only for /cards display."""
    if fee is None:
        return "Fee not listed"
    if fee == 0:
        return "Lifetime Free"
    if fee <= 1000:
        return "Entry"
    if fee <= 5000:
        return "Mid-range"
    if fee <= 12500:
        return "Super Premium"
    return "Luxury"

GOAL_KEYWORDS = {
    "cashback": ["cashback"],
    "travel-miles": ["airline transfer", "hotel transfer", "travel booking"],
    "reward-points": ["pay by points", "catalogue products"],
    "lifestyle-experience": ["experience", "catalogue brand vouchers"],
}

LOUNGE_KEYWORDS = {
    "domestic": ["domestic"],
    "international": ["international"],
    "railway": ["railway"],
}

# Composite score weights. Weights for factors the user didn't opt into
# (no lounge need, no lifestyle picks, no milestone appetite) are dropped
# and the remainder is renormalized — see _composite().
WEIGHTS = {
    "value": 0.50,
    "goal": 0.20,
    "lounge": 0.10,
    "lifestyle": 0.10,
    "milestone": 0.10,
}


def _matches_any(text, keywords):
    if not text:
        return False
    text = text.lower()
    return any(k in text for k in keywords)


def _fetch_candidates(conn, fee_cap, bank_id):
    q = """
        SELECT c.id, c.card_name, b.bank_name, c.bank_id, c.joining_fee,
               c.return_percentage, c.best_suited_for, c.overview
        FROM credit_cards c
        JOIN banks b ON b.id = c.bank_id
        WHERE 1=1
    """
    args = []
    if fee_cap is not None:
        q += " AND c.joining_fee IS NOT NULL AND c.joining_fee <= ?"
        args.append(fee_cap)
    if bank_id:
        q += " AND c.bank_id = ?"
        args.append(bank_id)
    return conn.execute(q, args).fetchall()


def _bulk_by_card(conn, table, cols, card_ids):
    """Fetch rows for many cards at once, grouped by card_id."""
    out = defaultdict(list)
    if not card_ids:
        return out
    chunk = 500
    col_sql = ", ".join(cols)
    for i in range(0, len(card_ids), chunk):
        ids = card_ids[i:i + chunk]
        placeholders = ",".join("?" * len(ids))
        rows = conn.execute(
            f"SELECT card_id, {col_sql} FROM {table} WHERE card_id IN ({placeholders})",
            ids,
        ).fetchall()
        for r in rows:
            out[r["card_id"]].append(r)
    return out


def _score_category_value(spend, earn_rows, return_pct_midpoint):
    """₹ estimated monthly reward value for one card given the user's spend."""
    monthly_value = 0.0
    matched_categories = []
    for cat_key, amount in spend.items():
        if cat_key == "other" or not amount:
            continue
        keywords = CATEGORY_KEYWORDS[cat_key]
        best_rate = 0.0
        for row in earn_rows:
            if row["has_rewards"] and _matches_any(row["category"], keywords):
                best_rate = max(best_rate, parse_effective_rate_percent(row["reward_rate"]))
        if best_rate > 0:
            matched_categories.append(CATEGORY_LABELS[cat_key])
        else:
            # No explicit category match — fall back to the card's overall
            # return range at a 50% discount since it isn't a guaranteed rate.
            best_rate = return_pct_midpoint * 0.5
        monthly_value += amount * (best_rate / 100)

    other_amount = spend.get("other", 0)
    if other_amount:
        monthly_value += other_amount * (return_pct_midpoint * 0.5 / 100)

    return monthly_value, matched_categories


def _score_goal(best_suited_for, return_pct_midpoint, primary_goal):
    keywords = GOAL_KEYWORDS.get(primary_goal, [])
    matched = _matches_any(best_suited_for, keywords)
    score = 70 if matched else 0
    score += min(return_pct_midpoint, 30)
    return min(score, 100), matched


def _score_lounge(lounge_rows, lounge_need):
    keywords = LOUNGE_KEYWORDS.get(lounge_need)
    if not keywords:
        return None
    for row in lounge_rows:
        if _matches_any(row["access_type"], keywords):
            return 100
    return 0


def _score_lifestyle(benefit_rows, wanted):
    if not wanted:
        return None, []
    matched_labels = []
    for want in wanted:
        for row in benefit_rows:
            if row["benefit_category"] and want.lower() in row["benefit_category"].lower():
                matched_labels.append(row["benefit_category"])
                break
    return (len(matched_labels) / len(wanted)) * 100, matched_labels


def _score_milestone(milestone_rows, appetite, total_monthly_spend, total_annual_spend):
    if appetite != "yes" or not milestone_rows:
        return None, []
    achievable = []
    for row in milestone_rows:
        target = row["milestone_spend"]
        if target is None:
            continue
        cycle = (row["cycle_type"] or "").lower()
        baseline = total_monthly_spend if cycle == "statement" else total_annual_spend
        if baseline >= target:
            achievable.append(row["milestone_benefit"] or row["milestone_name"])
    return (100 if achievable else 0), achievable


def _composite(parts):
    """parts: list of (weight_key, score_or_None). None = factor not applicable."""
    total_w, total_s = 0.0, 0.0
    for key, score in parts:
        if score is None:
            continue
        w = WEIGHTS[key]
        total_w += w
        total_s += w * score
    return (total_s / total_w) if total_w else 0.0


def recommend(conn, params):
    spend = {k: float(params.get("spend", {}).get(k) or 0) for k in CATEGORY_KEYWORDS}
    spend["other"] = float(params.get("spend", {}).get("other") or 0)
    total_monthly_spend = sum(spend.values())
    total_annual_spend = total_monthly_spend * 12

    fee_cap = FEE_CAPS.get(params.get("fee_budget"), None)
    bank_id = params.get("bank_preference") or None
    lounge_need = params.get("lounge_need") or "none"
    primary_goal = params.get("primary_goal") or ""
    lifestyle_wanted = params.get("lifestyle_benefits") or []
    milestone_appetite = params.get("milestone_appetite") or "no"

    widened = []
    candidates = _fetch_candidates(conn, fee_cap, bank_id)
    if len(candidates) < 5 and bank_id:
        widened.append("bank_preference")
        candidates = _fetch_candidates(conn, fee_cap, None)
    if len(candidates) < 5 and fee_cap is not None:
        widened.append("fee_budget")
        candidates = _fetch_candidates(conn, None, None)

    card_ids = [c["id"] for c in candidates]
    earn_by_card = _bulk_by_card(conn, "earn_categories",
                                  ["category", "reward_rate", "has_rewards"], card_ids)
    benefits_by_card = _bulk_by_card(conn, "benefits", ["benefit_category", "benefit_title"], card_ids)
    lounge_by_card = _bulk_by_card(conn, "lounge_access", ["access_type", "details"], card_ids)
    milestones_by_card = _bulk_by_card(conn, "milestones",
                                        ["milestone_name", "cycle_type", "milestone_spend", "milestone_benefit"],
                                        card_ids)

    # Lounge need is a hard filter too, but only applied if enough cards
    # still qualify — otherwise it's dropped and folded into the score instead.
    lounge_keywords = LOUNGE_KEYWORDS.get(lounge_need)
    if lounge_keywords:
        with_lounge = [c for c in candidates
                        if any(_matches_any(r["access_type"], lounge_keywords)
                               for r in lounge_by_card.get(c["id"], []))]
        if len(with_lounge) >= 5:
            candidates = with_lounge
        else:
            widened.append("lounge_need")

    scored = []
    for c in candidates:
        return_pct_mid = parse_return_percentage_midpoint(c["return_percentage"])
        earn_rows = earn_by_card.get(c["id"], [])
        monthly_value, matched_categories = _score_category_value(spend, earn_rows, return_pct_mid)
        annual_value = monthly_value * 12
        fee = c["joining_fee"] or 0
        net_annual_value = annual_value - fee

        goal_score, goal_matched = _score_goal(c["best_suited_for"], return_pct_mid, primary_goal)
        lounge_score = _score_lounge(lounge_by_card.get(c["id"], []), lounge_need)
        lifestyle_score, lifestyle_matched = _score_lifestyle(benefits_by_card.get(c["id"], []), lifestyle_wanted)
        milestone_score, milestones_hit = _score_milestone(
            milestones_by_card.get(c["id"], []), milestone_appetite,
            total_monthly_spend, total_annual_spend,
        )

        scored.append({
            "card_id": c["id"],
            "card_name": c["card_name"],
            "bank_name": c["bank_name"],
            "joining_fee": fee,
            "return_percentage": c["return_percentage"] or "NA",
            "best_suited_for": c["best_suited_for"] or "",
            "monthly_reward_value": round(monthly_value, 2),
            "annual_reward_value": round(annual_value, 2),
            "net_annual_value": round(net_annual_value, 2),
            "matched_categories": matched_categories,
            "goal_matched": goal_matched,
            "lifestyle_matched": lifestyle_matched,
            "milestones_hit": milestones_hit,
            "lounge_available": lounge_score == 100,
            "_parts": [
                ("value", None),  # filled in after normalization below
                ("goal", goal_score),
                ("lounge", lounge_score),
                ("lifestyle", lifestyle_score),
                ("milestone", milestone_score),
            ],
        })

    if scored:
        values = [s["net_annual_value"] for s in scored]
        lo, hi = min(values), max(values)
        span = (hi - lo) or 1.0
        for s in scored:
            value_score = ((s["net_annual_value"] - lo) / span) * 100
            s["_parts"][0] = ("value", value_score)
            s["score"] = round(_composite(s["_parts"]), 1)
            del s["_parts"]

    scored.sort(key=lambda s: (-s["score"], -s["net_annual_value"]))
    top5 = scored[:5]

    for s in top5:
        s["reasons"] = _build_reasons(s, primary_goal, lounge_need)

    return {
        "results": top5,
        "widened_filters": widened,
        "total_monthly_spend": total_monthly_spend,
        "total_annual_spend": total_annual_spend,
        "candidate_count": len(candidates),
    }


def _build_reasons(s, primary_goal, lounge_need):
    reasons = []
    if s["matched_categories"]:
        reasons.append("Earns rewards on " + ", ".join(s["matched_categories"]))
    reasons.append(f"Estimated reward value ~₹{s['annual_reward_value']:.0f}/year "
                    f"(net ₹{s['net_annual_value']:.0f} after joining fee)")
    if s["goal_matched"]:
        reasons.append(f"Matches your goal: {primary_goal.replace('-', ' ')}")
    if lounge_need != "none" and s["lounge_available"]:
        reasons.append(f"Offers {lounge_need} lounge access")
    if s["lifestyle_matched"]:
        reasons.append("Lifestyle perks: " + ", ".join(sorted(set(s["lifestyle_matched"]))[:4]))
    if s["milestones_hit"]:
        reasons.append("Milestone within reach: " + s["milestones_hit"][0])
    if s["net_annual_value"] < 0:
        reasons.append("Note: joining fee may not be justified by your current spend")
    return reasons
