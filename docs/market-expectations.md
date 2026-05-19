# Market Expectations

This is the **single source of truth** for market/locale-specific
assumptions used by every agent. Agents reference this file by name;
they do not hardcode rules. If you disagree with a check, edit this
file rather than the agent files.

The valid market values are: `lebanon`, `gcc`, `mena`, `eu`, `us`,
`uk`, `global`.

Markets are auto-detected from the URL's TLD by
`scripts/fetch_page.py` (`--market` argument). The TLD→market mapping
is also defined in code (`TLD_TO_MARKET` in `scripts/fetch_page.py`)
and must stay in sync with the country lists below.

When a check below is marked **TBD — verify with local user**, treat
findings on that signal as MEDIUM at most. Do not flag CRITICAL on
guesses.

---

## lebanon

Lebanon's e-commerce landscape is shaped by banking-sector
restrictions, severe currency volatility, and WhatsApp-centric
customer service. Treat Lebanon separately from MENA/GCC — many
"MENA-wide" assumptions are wrong here.

**Payment methods**
- COD is the dominant payment method. Flag **CRITICAL** if not offered.
- Whish Pay is the primary local digital payment gateway. Flag
  **HIGH** if not offered.
- Credit card (Visa/Mastercard) checkout is limited in practice due to
  banking restrictions. Do **NOT** penalize stores that lack
  Visa/Mastercard. Do flag **HIGH** if a store offers **ONLY** card
  (excludes most local buyers).

**Pricing**
- USD pricing alongside LBP is expected given currency volatility.
  Flag **HIGH** if only one currency is shown.

**Customer service**
- WhatsApp contact is effectively required. Flag **CRITICAL** if
  missing.

**Language**
- Arabic/RTL support is a **bonus**, not required. Lebanese
  e-commerce is predominantly English/French. Do not penalize absence.

**Delivery**
- Named local delivery partner (Wakilni, Toters, Bosta, or equivalent)
  expected. Flag **MEDIUM** if no partner is mentioned anywhere.

---

## gcc

Covers UAE, Saudi Arabia, Kuwait, Qatar, Bahrain, Oman.

**Payment methods**
- Tabby and Tamara BNPL are expected. Flag **HIGH** if absent.
- COD is still common but declining. Not having COD is **MEDIUM**, not
  CRITICAL.
- Apple Pay is widely adopted. Flag **HIGH** if absent.
- Saudi: Mada is the dominant local card scheme — flag **HIGH** if not
  accepted on a .sa store.
- Country-specific card scheme support beyond Mada/Tabby/Tamara: TBD
  — verify with local user.

**Language**
- Arabic / RTL support is **required**, not optional. Flag **CRITICAL**
  if missing.

**Pricing**
- VAT-inclusive display required in UAE, Saudi Arabia, Bahrain
  (jurisdictions with consumer VAT). Flag **HIGH** if missing.

---

## mena

Covers Egypt, Jordan, Morocco, Tunisia, Algeria (non-GCC Arab states).

**Payment methods**
- Egypt: Fawry payment network (cash via retail kiosks + bill-pay) is
  expected. Flag **HIGH** if absent on an .eg store.
- COD is expected across all countries in this group. Flag **HIGH**
  if absent.
- Local card scheme support varies by country: TBD — verify with
  local user. Do not flag CRITICAL on a guess.
- Morocco / Tunisia / Algeria: specific BNPL and wallet expectations
  — TBD — verify with local user.

**Language**
- Arabic / RTL support is **required**. Flag **CRITICAL** if missing.
- Morocco / Tunisia: French is also widely used; bilingual FR/AR
  storefronts are common.

---

## eu

Covers Germany, France, Spain, Italy, Netherlands, Belgium (and other
EU member states by extension).

**Pricing**
- VAT-inclusive display required by EU Consumer Rights Directive.
  Flag **CRITICAL** if prices shown excluding VAT to consumers.

**Legal / Compliance**
- GDPR cookie banner required if any cookies beyond strictly necessary
  are set. Flag **HIGH** if missing.
- Returns policy ≥ 14 days visible (legal minimum under EU Consumer
  Rights Directive). Flag **CRITICAL** if absent or shorter.

**Payment methods**
- SEPA bank transfer option expected. Flag **HIGH** if absent.
- Klarna / Afterpay / PayPal expected. Flag **HIGH** if none present.
- Country-specific schemes (iDEAL in NL, Bancontact in BE, Sofort in
  DE, etc.): TBD — verify with local user before flagging as
  required.

---

## us

**Pricing**
- Tax-exclusive pricing is acceptable and standard.
- Free-shipping thresholds typically land in the $35–$50 range. Flag
  **MEDIUM** if no free-shipping threshold is offered.

**Payment methods**
- Shop Pay, PayPal, and Apple Pay are expected. Flag **HIGH** if
  none of the three are present.
- Klarna / Afterpay / Affirm increasingly expected on AOV > $50. Flag
  **MEDIUM** if absent in that AOV band.

**Legal / Compliance**
- ADA accessibility lawsuits are a real risk. See accessibility
  coverage in `ecom-cro`, `ecom-products`, `ecom-mobile`.
- CCPA / state privacy disclosures: TBD — verify with local user.

---

## uk

**Pricing**
- VAT-inclusive display required. Flag **CRITICAL** if shown
  excluding VAT to consumers.

**Legal / Compliance**
- Returns policy ≥ 14 days visible (legal minimum under Consumer
  Contracts Regulations 2013). Flag **CRITICAL** if absent or shorter.

**Shipping**
- Royal Mail / Evri / DPD tracking expected. Flag **HIGH** if no
  named carrier or tracking is mentioned.

**Payment methods**
- PayPal, Klarna, Clearpay expected. Flag **HIGH** if none present.

---

## global

No market detected. Apply only universal checks. Do not enforce
locale-specific payment methods, language requirements, or pricing
display rules. Flag the absence of market detection as a note (not a
deduction) — a global storefront is a deliberate choice, not
necessarily a defect.

---

## How agents should use this

1. Receive the `market` parameter (string) from the orchestrator.
2. Apply only the rules under that market's section above.
3. If `market = global`, skip locale-conditional checks.
4. Never invent a market-specific rule that isn't in this file. If a
   merchant asks why a check was applied, the answer should be a
   pointer to a section here.
5. If a rule is marked **TBD — verify with local user**, output a
   MEDIUM-severity observation, not a CRITICAL.

Update this file (not the agent files) when a market's landscape
shifts — e.g. a new BNPL becomes table stakes, a new privacy law
lands, or a new payment rail goes live.
