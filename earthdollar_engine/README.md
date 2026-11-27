# EarthDollar Engine v0.1

Experimental water-time reference unit. No real currency, guarantee, investment, or water ownership is created.

## Run
Open `EarthDollar.html` in a modern browser. No server, installation, account, or network is needed. Close at any time; use Export scenario to save inputs first. Import scenario restores a saved JSON. Source code is embedded in the HTML. The app never sends data anywhere.

## Model
- Fixed protocol benchmark q = 3 liters per human-day by default (illustrative, not medical advice). Changing it creates a different denomination; all historical rows are recalculated using the chosen q.
- Reference value V = q × tariff USD/m³ / 1000. Other currency estimates use manually entered local currency per USD. This is an accounting proxy, not a trading or redemption rate.
- Price history uses one consistent series per basis: potable-only or combined/unspecified municipal tariff proxy. Index = 100 × price / first positive price in selected series. Zero values are allowed, but USD-to-E$ conversion is undefined at zero. No interpolating or fabricating history.
- Reserve scenario: usable supply = max(0, safe inventory + (net daily sustainable inflow − protected daily allocation) × horizon), subject to an optional gross delivery limit net of protected allocation. Net daily inflow must already account for treatment losses, ecological constraints and existing non-protected commitments. This simple horizon model does not prove daily feasibility, geographic delivery, safety, or legal title; only verified deliverable surplus could support claims. Inventory and flow cannot be double counted.
- Reserve ceiling = usable liters / q. Coverage = ceiling / outstanding E$ obligations. No automatic issuance, minting or redemption. Basic access must be protected before reserve claims. Zero outstanding obligations has no defined coverage ratio.

## Historical input
Import a UTF-8 CSV with exactly these columns (order may vary):
`date,series,basis,usd_per_m3,source`
Date is ISO YYYY-MM-DD. One row per date and series. Basis is `potable_only` or `municipal_proxy`; each series must use one basis consistently. Source is required (a URL or provenance description). Prices must be nonnegative finite numbers. Import replaces the current dataset; export CSV first to preserve it. Aggregate only genuinely comparable observations before import; never mix water-only and combined tariffs, or different weighting/consumption conventions, into one series.

Bundled source: Global Water Intelligence press release, 2026-10-29, population-weighted average USD 1.67/m³. It is labeled municipal proxy because the published aggregate does not establish a potable-only delivered marginal cost. No older observations are bundled, so a real backtest requires additional comparable data. Full GWI dataset is membership restricted. Potential alternative: World Bank IBNET (https://newibnet.org/use-data). Public reproducibility catalog: https://reproducibility.worldbank.org/catalog/484.

## Verify
Run `node test_engine.js` (Node.js required only for tests, not the app). This tests the same pure calculation code embedded in the HTML, including edge cases and import validation. Browser compatibility and reserve audits are not certified.
