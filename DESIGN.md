---
name: Wandor
description: AI trip planner — video-hero landing over a warm, restrained Operate flow
colors:
  wandor-dark: "#0a0a0a"
  wandor-text: "#1a1a1a"
  wandor-muted: "#767676"
  wandor-muted-small: "#5c5c5c"
  wandor-prompt: "#905831"
  surface-white: "#ffffff"
  glass-fill: "rgba(255,255,255,0.06)"
typography:
  display:
    fontFamily: "Special Elite, serif"
    fontSize: "40px"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: "normal"
  headline:
    fontFamily: "Geist, sans-serif"
    fontSize: "clamp(40px, 6vw, 68px)"
    fontWeight: 500
    lineHeight: 1.05
    letterSpacing: "-0.04em"
  body:
    fontFamily: "Geist, sans-serif"
    fontSize: "20px"
    fontWeight: 500
    lineHeight: 1.625
  label:
    fontFamily: "Geist, sans-serif"
    fontSize: "15px"
    fontWeight: 500
    letterSpacing: "0.04em"
rounded:
  pill: "9999px"
  card: "44px"
  control: "9999px"
spacing:
  section-x: "80px"
  section-x-mobile: "24px"
  card-gap: "32px"
components:
  button-primary:
    backgroundColor: "{colors.wandor-dark}"
    textColor: "#fafafa"
    rounded: "{rounded.pill}"
    padding: "14px 20px"
  button-primary-hover:
    backgroundColor: "#333333"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.wandor-text}"
    typography: "{typography.label}"
---

# Design System: Wandor

## Overview

**Creative North Star: "The Passport Stamp on Frosted Glass"**

Wandor opens with a full-viewport, ambient looping travel video and a single liquid-glass card floating over it — the product's entire pitch (describe your trip, get a plan) compressed into one legible object over motion. Past the hero, the same restraint carries into the working flow: the video and glass are the hero's signature, not a decoration repeated everywhere; the planning steps that follow (budget, preferences, itinerary) run on a quiet cream-and-ink system so the traveler can actually fill out a form and read a day-by-day plan without fighting the atmosphere. Special Elite (the typewriter serif) is reserved strictly for the "wandor" wordmark — a single, deliberate handwritten-ticket accent against an otherwise clean Geist interface. Terracotta (`#905831`) is the one warm color in the system and it is spent narrowly: the traveler's own words in the prompt card, and small emphasis/active moments in the flow, never backgrounds or large fills.

**Key Characteristics:**
- One video/glass moment at the very top of the funnel; everything after it is flat, quiet, and legible.
- Geist carries all real UI and body text; Special Elite never appears outside the wordmark.
- Terracotta is a narrow accent (text emphasis, active/selected states), not a fill color.
- Primary actions are always a black pill (`rounded-full`, `bg-wandor-dark`); there is no secondary button color — hierarchy comes from filled vs. ghost, not from a second hue.
- Liquid glass (`bg-white/[0.06]`, thick white border, heavy blur) is reused as the container language for cards throughout the flow, without the video — it reads as "the Wandor card," not "the Wandor video effect."

## Colors

Restrained strategy: near-black, near-white neutrals plus a single terracotta accent, spent narrowly.

### Primary
- **Wandor Terracotta** (`#905831`): the one warm accent. Used for the traveler's own input text (hero prompt), and for active/selected/emphasis states in the planning flow (selected chips, current step indicator, highlighted totals). Never a background fill.

### Neutral
- **Wandor Ink** (`#0a0a0a`): primary CTA fill, wordmark, highest-emphasis text.
- **Wandor Text** (`#1a1a1a`): default body and heading text.
- **Wandor Muted** (`#767676`): secondary text, subtitles, helper copy.
- **Surface White** (`#ffffff`): page ground for every screen after the hero.
- **Glass Fill** (`rgba(255,255,255,0.06)` on a `3px` white border): the liquid-glass card fill, always over the hero video or a soft neutral backdrop — never over plain white with nothing behind it, or the blur has nothing to distort.

### Named Rules
**The One Video Rule.** The looping background video and its glass-over-motion treatment exist only on the landing hero. The planning flow (budget, preferences, results) never reintroduces video or a dark backdrop — it runs on flat white.
**The Narrow Terracotta Rule.** `#905831` never fills a background or a button. It colors text and small active-state accents only.

## Typography

**Display Font:** Special Elite (with serif fallback) — wordmark only, never body copy.
**Body Font:** Geist (with sans-serif fallback), weights 400/500/600/700.

**Character:** A typewriter-ticket wordmark against an otherwise contemporary, geometric sans — the tension between "handwritten travel journal" and "clean modern product" is the whole pairing.

### Hierarchy
- **Display** (400, 40px / 32px mobile, leading-none): the "wandor" wordmark, nowhere else.
- **Headline** (500, `clamp(40px,6vw,68px)`, leading 1.05, tracking -0.04em): hero H1 and step-level page titles.
- **Title** (600, 24–28px): section headers within the planning flow (e.g. "Your budget breakdown").
- **Body** (500, 20px, leading relaxed): hero subtitle and primary reading copy; 65–75ch measure on the itinerary results.
- **Label** (500, 15px, tracking 0.04em, uppercase): nav links, ghost buttons, pill button text.

### Named Rules
**The Wordmark-Only Rule.** Special Elite renders the word "wandor" and nothing else — not section headers, not pull quotes, not "fun" accents elsewhere.

## Layout

Hero: full-`min-h-svh` single section, content capped at `max-w-[1360px]`, centered, nav at `px-20`/mobile `px-6`. Planning flow: a narrower centered column (`max-w-[720px]`) so multi-field forms and the day-by-day itinerary stay a comfortable reading/scanning width; each step is its own screen (not a giant single-page form), with a persistent top-of-column step indicator (Details → Preferences → Itinerary). Mobile breakpoint at `760px` (Tailwind `max-md`) collapses nav links and the login button, drops the wordmark to 32px, and lets the glass card go full-bleed-minus-margin (`calc(100vw-48px)`).

## Elevation & Depth

Two distinct depth languages, deliberately not shared:
- **Hero:** heavy `backdrop-blur` (glass) is the entire depth vocabulary — no drop shadows, because the card reads as sitting *in* the video, not floating above a flat page.
- **Flow pages:** flat by default; a soft, low-opacity shadow (`0 0 4px rgba(0,0,0,0.15)`, matching the hero card's own shadow value) appears only on the active/focused step card, never as ambient decoration on every panel.

### Named Rules
**The Blur-Is-Depth Rule.** Backdrop blur is Wandor's elevation system on glass surfaces; don't add a drop shadow underneath a blurred card as well — pick one.

## Shapes

Everything rounds toward a pill: buttons and inputs are `rounded-full`, cards use a large `44px` radius (soft rectangle, not a pill) so they read as containers rather than controls. No sharp corners anywhere in the system; no corner radius smaller than 16px on any surface a user reads text inside.

## Components

### Buttons
- **Shape:** full pill (`rounded-full`).
- **Primary:** `bg-wandor-dark` (#0a0a0a), text `#fafafa`, `px-5 py-3.5` (nav) or the larger `156×56` CTA size inside the prompt card; uppercase label, `tracking-[0.02–0.04em]`.
- **Hover / Focus:** `hover:bg-[#333]`, `active:scale-95` — the only motion a button gets.
- **Ghost (nav links):** transparent background, `text-wandor-text`, `hover:opacity-55`. No secondary-colored button anywhere in the system.

### Cards (liquid glass) — hero only
- **Corner Style:** `44px` radius.
- **Background:** `bg-white/[0.06]` with a `3px` solid white border and `backdrop-blur-[20px]`.
- **Shadow:** `0 0 4px rgba(0,0,0,0.15)`.
- **Use:** the hero prompt card, exclusively. This is the hero's signature effect, not a general container.

### Cards (flow pages) — flat
- **Corner Style:** `44px` radius, matching the hero's card language without borrowing its material.
- **Background:** solid white, `1px` neutral border (`border-black/[0.08])`. No blur, no translucency — there's no video to soften against off-hero.
- **Shadow:** flat at rest; the single active/focused card in view (the current step's form, or an open day accordion) gets `0 0 4px rgba(0,0,0,0.15)` — the same shadow value as the hero card, so elevation still reads as "this is the Wandor system," just without the blur.
- **Use:** trip-details form, preferences form, cost-estimate summary, itinerary intro, and each day accordion in the results step.

### Inputs / Fields
- **Style:** pill-shaped text inputs on the flow pages, `wandor-text` label above (associated via `htmlFor`/`id`), helper text below in `#5c5c5c` (a darker neutral than `wandor-muted`, kept AA-compliant at small sizes — `wandor-muted` itself stays reserved for ≥18px text, per its hero usage).
- **Focus:** a 2px `wandor-dark` outline offset from the field, no color-shifted border.
- **Selected/active (chips, radio pills, rating dots):** terracotta text/border only — dots use a terracotta ring on white, never a terracotta fill.

### Dropdowns (custom, not native `<select>`)
- **Why:** a native `<select>`'s open option list is OS-rendered and can't be themed — it breaks the system the moment it opens. Every dropdown in the flow is a custom listbox (built on Radix `Select` for correct keyboard/ARIA behavior) styled end-to-end instead.
- **Trigger:** identical pill shape/border to text inputs, with a `ChevronDown` icon at the trailing edge; focus/open state gets the same 2px `wandor-dark` ring.
- **Panel:** white background, `1px` neutral border, `16px` radius (a smaller, list-appropriate radius than the `44px` card radius), the same soft shadow value as an elevated card (`0 0 4px rgba(0,0,0,0.15)`); width matches the trigger but can grow up to `320px` so longer option text (e.g. cost ranges) doesn't wrap unnecessarily.
- **Options:** hovered/keyboard-highlighted option gets a quiet `black/[0.04]` background (neutral, not terracotta — fills stay off-limits). The selected option is marked by terracotta text plus a small terracotta check icon, never a filled row.

### Navigation
- Logo (Special Elite, 40px/32px) far left; center-absolute nav links (Discover / Pricing / FAQs) hidden below 760px; Login (ghost) + Plan My Trip (primary pill) on the right, Login hidden below 760px.

## Do's and Don'ts

### Do:
- **Do** keep Special Elite confined to the single word "wandor."
- **Do** treat the black pill as the only primary-action shape across the whole product, hero through results.
- **Do** let terracotta carry emphasis through text color and small active accents only.
- **Do** carry the `44px` card radius past the hero, but as a flat white card — not the glass material itself.

### Don't:
- **Don't** put the looping video or a dark backdrop anywhere past the landing hero.
- **Don't** fill a button, background, or large surface with terracotta.
- **Don't** add a second accent color to the flow pages "for variety" — the palette stays this narrow on purpose.
- **Don't** stack a drop shadow under a blurred glass card; blur is the depth cue.
