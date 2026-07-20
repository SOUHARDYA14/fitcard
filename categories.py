"""Maps the friendly spend categories shown on the params form to the messy,
scraped `earn_categories.category` strings in the DB, and parses free-text
`reward_rate` values into a comparable effective rate.

The DB has 475 distinct category labels (a mix of real spend categories, brand
names, and stray spend-threshold artifacts like "2.5L - 5L" from complex reward
tables). Keyword matching against real-world phrasing is the only viable
approach without a hand-curated mapping table for all 720 cards.
"""
import re

# user-facing category -> substrings matched case-insensitively against
# earn_categories.category
CATEGORY_KEYWORDS = {
    "fuel": ["fuel", "hpcl", "bpcl", "iocl", "jio-bp", "petrol"],
    "dining": ["dining", "restaurant", "zomato", "swiggy", "food delivery",
               "domino", "pizza hut", "kfc", "fast food", "qmin", "eazydiner"],
    "grocery": ["grocery", "supermarket", "bigbasket", "blinkit", "zepto",
                "dmart", "reliance smart", "reliance retail", "jio mart",
                "star bazaar", "spar", "departmental store", "wholesale"],
    "rent": ["rent"],
    "utilities": ["utilit", "bbps", "bill payment", "electricity", "telecom",
                  "recharge", "dth", "broadband", "cable"],
    "upi": ["upi"],
    "online": ["online", "e-commerce", "amazon", "flipkart", "myntra", "ajio",
               "nykaa", "meesho", "tata cliq", "shopping"],
    "travel": ["travel", "flight", "hotel", "airline", "railway", "trains",
               "irctc", " cab", "cab(", "cab ", "taxi", "uber", "ola",
               "makemytrip", "yatra", "cleartrip", "ixigo", "oyo",
               "duty free", "holiday", " bus"],
    "insurance": ["insurance", "lic"],
    "education": ["education"],
}

CATEGORY_LABELS = {
    "fuel": "Fuel", "dining": "Dining", "grocery": "Grocery", "rent": "Rent",
    "utilities": "Utilities", "upi": "UPI", "online": "Online Shopping",
    "travel": "Travel", "insurance": "Insurance", "education": "Education",
}

# Assumed redemption value of one reward point, in rupees. There is no
# redemption_options data in the DB to derive this per-card, so we use a
# single documented industry-average figure (~₹0.20-0.25/point is typical for
# base-tier Indian cards). This is surfaced to users as a caveat in the UI.
RUPEE_PER_REWARD_POINT = 0.25

# Accelerated-category multipliers in scraped text can be extreme (20x+ promo
# rates) and usually carry spend caps the DB doesn't record. Cap the derived
# effective rate so one outlier row can't dominate the score.
MAX_EFFECTIVE_RATE_PERCENT = 10.0

_RP_RATE_RE = re.compile(
    r"Earn\s+([\d.]+)\s+Reward Points?\s+per\s+₹\s*([\d.]+)\s+spent", re.I
)
_PERCENT_RE = re.compile(r"([\d.]+)\s*%")


def parse_effective_rate_percent(reward_rate):
    """Convert a reward_rate string into an effective %-of-spend value."""
    if not reward_rate:
        return 0.0

    m = _RP_RATE_RE.search(reward_rate)
    if m:
        points, per_rupees = float(m.group(1)), float(m.group(2))
        if per_rupees <= 0:
            return 0.0
        rate = (points / per_rupees) * RUPEE_PER_REWARD_POINT * 100
        return min(rate, MAX_EFFECTIVE_RATE_PERCENT)

    m = _PERCENT_RE.search(reward_rate)
    if m:
        return min(float(m.group(1)), MAX_EFFECTIVE_RATE_PERCENT)

    return 0.0


def parse_return_percentage_midpoint(return_percentage):
    """'1% to 3%' -> 2.0 ; '3%' -> 3.0 ; None/'NA' -> 0.0"""
    if not return_percentage:
        return 0.0
    nums = [float(n) for n in re.findall(r"[\d.]+", return_percentage)]
    if not nums:
        return 0.0
    return sum(nums) / len(nums)
