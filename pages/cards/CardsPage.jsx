import React, { useMemo, useState } from "react";
import "../../styles/tokens.css";
import { Navbar, Input, Badge, AmbientBackground } from "../../components";
import { tierKeyFromLabel } from "../../constants";
import "./CardsPage.css";

/**
 * React port of templates/cards.html. Route/data unchanged — app.py's
 * all_cards() still queries and passes `cards` exactly as before; this
 * only replaces the template's inline <style> + hand-written body +
 * inline <script>. Ported as closely to the legacy behavior as
 * reasonable: same search/sort semantics (including "no listed fee
 * sorts last regardless of direction"), same empty-state copy, same
 * tier-dot coloring (constants/tiers.js's TIER_DOT_COLORS — the
 * list-view mapping, deliberately distinct from the recommendation
 * card's gradient mapping; see docs/COMPONENT_AUDIT.md).
 *
 * @param {Array<{card_name:string, bank_name:string, joining_fee:number|null, return:string, tier:string, best_suited_for:string|null}>} cards
 */
export default function CardsPage({ cards }) {
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("fee-asc");

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    let items = cards.filter(
      (c) =>
        !q ||
        c.card_name.toLowerCase().includes(q) ||
        c.bank_name.toLowerCase().includes(q)
    );

    items = items.slice().sort((a, b) => {
      // Cards with no listed fee always sort last, regardless of direction.
      if (sort === "fee-asc")
        return (a.joining_fee ?? Infinity) - (b.joining_fee ?? Infinity);
      if (sort === "fee-desc")
        return (b.joining_fee ?? -Infinity) - (a.joining_fee ?? -Infinity);
      if (sort === "name-asc") return a.card_name.localeCompare(b.card_name);
      if (sort === "bank-asc") return a.bank_name.localeCompare(b.bank_name);
      return 0;
    });

    return items;
  }, [cards, search, sort]);

  function money(n) {
    return n == null ? "—" : "₹" + Number(n).toLocaleString("en-IN");
  }

  return (
    <div className="cardspage-wrap">
      <AmbientBackground />
      <Navbar
        variant="back-link"
        brandHref="/"
        backLinks={[
          { href: "/match", label: "← Back to matcher" },
          { href: "/insurance", label: "Insurance" },
        ]}
      />

      <div className="cardspage-intro">
        <div className="cardspage-spine" />
        <div>
          <h1 className="cardspage-h1">All cards in the database.</h1>
          <p className="cardspage-sub">
            {cards.length} cards total. Search or sort to browse everything —
            not just your top 5 matches.
          </p>
        </div>
      </div>

      <div className="cardspage-controls">
        <Input
          id="search"
          variant="underline"
          label="Search"
          placeholder="Card name or bank…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="cardspage-search"
          fieldClassName="cardspage-search-field"
        />
        <Input
          id="sort"
          as="select"
          variant="underline"
          label="Sort by"
          value={sort}
          onChange={(e) => setSort(e.target.value)}
        >
          <option value="fee-asc">Fee: low to high</option>
          <option value="fee-desc">Fee: high to low</option>
          <option value="name-asc">Name: A to Z</option>
          <option value="bank-asc">Bank: A to Z</option>
        </Input>
      </div>

      <div className="cardspage-count">
        {filtered.length} card{filtered.length === 1 ? "" : "s"} shown
      </div>

      <div className="cardspage-list">
        {filtered.length === 0 ? (
          <div className="cardspage-empty">No cards match "{search}".</div>
        ) : (
          filtered.map((c, idx) => (
            <div className="cardspage-row" key={`${c.card_name}-${c.bank_name}`}>
              <div className="cardspage-row-main">
                <span className="cardspage-row-index">
                  {String(idx + 1).padStart(2, "0")}
                </span>
                <div className="cardspage-row-text">
                  <span className="cardspage-row-name">{c.card_name}</span>
                  <span className="cardspage-row-bank">{c.bank_name}</span>
                  {c.best_suited_for && (
                    <span className="cardspage-row-suited">
                      {c.best_suited_for}
                    </span>
                  )}
                </div>
              </div>
              <div className="cardspage-row-stats">
                <div className="cardspage-stat">
                  <span className="cardspage-stat-label">Fee</span>
                  <span className="cardspage-stat-val">
                    {money(c.joining_fee)}
                  </span>
                </div>
                <div className="cardspage-stat">
                  <span className="cardspage-stat-label">Return</span>
                  <span className="cardspage-stat-val">{c.return}</span>
                </div>
                <Badge variant="tier" tier={tierKeyFromLabel(c.tier)}>
                  {c.tier}
                </Badge>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
