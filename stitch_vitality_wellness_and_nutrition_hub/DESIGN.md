---
name: NutriVibe Living System
colors:
  surface: '#f9f9ff'
  surface-dim: '#d3daef'
  surface-bright: '#f9f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f1f3ff'
  surface-container: '#e9edff'
  surface-container-high: '#e1e8fd'
  surface-container-highest: '#dce2f7'
  on-surface: '#141b2b'
  on-surface-variant: '#3d4a42'
  inverse-surface: '#293040'
  inverse-on-surface: '#edf0ff'
  outline: '#6d7a72'
  outline-variant: '#bccac0'
  surface-tint: '#006c4a'
  primary: '#006948'
  on-primary: '#ffffff'
  primary-container: '#00855d'
  on-primary-container: '#f5fff7'
  inverse-primary: '#68dba9'
  secondary: '#006c4b'
  on-secondary: '#ffffff'
  secondary-container: '#64f9bc'
  on-secondary-container: '#00714e'
  tertiary: '#825100'
  on-tertiary: '#ffffff'
  tertiary-container: '#a36700'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#85f8c4'
  primary-fixed-dim: '#68dba9'
  on-primary-fixed: '#002114'
  on-primary-fixed-variant: '#005137'
  secondary-fixed: '#68fcbf'
  secondary-fixed-dim: '#45dfa4'
  on-secondary-fixed: '#002114'
  on-secondary-fixed-variant: '#005137'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#f9f9ff'
  on-background: '#141b2b'
  surface-variant: '#dce2f7'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.015em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  title-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
  label-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.04em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-sm: 1rem
  margin: 2rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system expresses vitality, scientific clarity, and mindful nourishment. It is designed for wellness seekers, nutritionists, and everyday health trackers who value clarity and uplifting momentum over medical austerity or cold gamification.

The aesthetic philosophy centers on **Luminous Biophilic Modernism**—a blend of modern clean interfaces, soft organic geometry, airy negative space, and vibrant nature-derived accents. The interface feels clean, restorative, and optimistic, instilling calm confidence and motivation with every interaction.

## Colors

The color palette reflects natural vitality balanced by neutral structure:

- **Primary (`#059669` - Emerald Deep):** Grounded botanical authority, used for primary actions, critical brand touchpoints, active states, and navigation headers.
- **Secondary (`#34D399` - Mint Breeze):** Energetic, crisp highlight tone for charts, positive trend chips, progress indicators, and active badges.
- **Tertiary (`#F59E0B` - Honey Amber):** Warm metabolic energy, reserved for micro-goals, streak counts, warnings, nutrition balance badges, and nutritional focus highlights.
- **Neutral Surface & Text (`#111827` to `#F9FAFB`):** Surfaces rely on clean porcelain and cool mist tones (`#FFFFFF`, `#F9FAFB`, and `#F3F4F6`), preserving contrast and daylight brightness. Primary typography uses deep charcoal (`#111827`), avoiding harsh absolute blacks while maintaining WCAG AAA accessibility.

Soft mint-tinted washes (`#ECFDF5`) are paired with emerald borders (`#A7F3D0`) to denote interactive focus and positive completion cards.

## Typography

The pairing combines **Plus Jakarta Sans** for headings, metrics, and interactive controls with **Inter** for data grids, nutritional facts, and body copy. 

- **Display & Headings:** Plus Jakarta Sans provides geometric warmth, high x-height, and optimistic curves that soften analytical data. Large headers use subtle negative tracking (`-0.02em`) to maintain editorial punch.
- **Body & Data:** Inter guarantees high-density legibility when rendering complex dietary breakdowns, ingredient glossaries, and micro-metric logs.
- **Labels & Badges:** Plus Jakarta Sans in semibold/bold weights with slight positive tracking ensures rapid scanning across meal tags and macro metrics.

## Layout & Spacing

This design system uses a responsive 12-column grid layout across desktop (max-width `1280px`), adapting to an 8-column layout on tablet (`768px - 1024px`) and a 4-column layout on mobile devices (`<768px`).

- **Grid & Alignment:** Canvas margins shrink from `2rem` on desktop to `1rem` on mobile. Gutters stay uniform at `1.5rem` on desktop and scale to `1rem` on handheld screens to preserve reading territory.
- **Rhythm & White Space:** Spacing is generous. Cards and modules utilize `space-lg` (`1.5rem`) internal padding to create open, breathable surfaces that prevent nutritional data clutter.
- **Vertical Flow:** Section splits deploy `space-xl` (`2.5rem`) to maintain clear topical grouping between meal plans, biometric charts, and interactive widgets.

## Elevation & Depth

Visual hierarchy uses a hybrid strategy of **Tonal Layering** and **Botanical Ambient Shadows**:

- **Surface Layers:** The background canvas rests on `#F9FAFB`. Secondary surface cards sit on solid `#FFFFFF`. Embedded modules (such as macronutrient breakdown cells) use soft cool gray `#F3F4F6` or faint emerald mist `#ECFDF5`.
- **Ambient Green Cast Shadows:** Standard cards use soft, high-diffusion shadows with a subtle cool-emerald undertone (`rgba(5, 150, 105, 0.04) 0px 8px 24px -4px, rgba(17, 24, 39, 0.03) 0px 2px 6px -1px`).
- **Floating Modals & Sheets:** Elevated navigation docks and interactive meal logging overlays use deeper drop diffusion (`rgba(5, 150, 105, 0.08) 0px 20px 32px -8px, rgba(17, 24, 39, 0.06) 0px 6px 12px -2px`).
- **Low-Contrast Structural Borders:** Every card features an ultra-thin 1px border (`#E5E7EB` or `#D1FAE5` on active cards) to preserve structure in both high and low display contrast environments.

## Shapes

The shape hierarchy follows friendly, continuous, and approachable geometry:

- **Standard Cards & Modals:** Standard corners use `rounded-lg` (16px) to `rounded-xl` (24px) for prominent containers, giving cards a soft, human feel.
- **Buttons & Action Controls:** Primary action buttons use 12px to 16px soft radii for balanced ergonomics.
- **Pill Elements:** Interactive chips, filter pills, calorie badges, and status indicator dots use full pill radii (`9999px`) to distinguish categorical tags from layout cards.

## Components

### Buttons
- **Primary:** Background `#059669` with pure white text, 12px rounded corners, bold typography (`label-lg`), and an ambient emerald drop shadow. On hover, shifts to `#047857` with slight scale (`1.01`).
- **Secondary:** Surface `#ECFDF5`, text `#059669`, border 1px solid `#A7F3D0`. Hover states trigger `#D1FAE5`.
- **Tertiary / Ghost:** Transparent background, charcoal `#111827` text, with light hover fill of `#F3F4F6`.

### Chips & Badges
- **Pill Badges:** Fully rounded (`rounded-full`), height 28px–32px. Category chips (e.g., "Keto", "High Protein", "Hydration") use light mint, amber, or mist backgrounds with high-contrast text.
- **Active Filter Chips:** Solid `#059669` background with white text and an integrated dismiss cross icon.

### Form Fields & Inputs
- **Base Input:** White background `#FFFFFF`, 12px rounded borders, 1px `#D1D5DB` stroke, height 48px, padded with `1rem` horizontally.
- **Focused State:** 1px stroke changes to `#059669` paired with an outward soft focus halo (`0 0 0 4px rgba(16, 185, 129, 0.15)`). Placeholder text rests in calm cool gray `#9CA3AF`.

### Checkboxes & Radios
- **Checkboxes:** 20px by 20px with 6px rounded corners. Unchecked has a 1.5px border of `#D1D5DB`. Checked state has a solid `#059669` fill with a crisp white checkmark icon.
- **Radio Buttons:** Outer ring 20px with centered 8px solid dot in `#059669` on white canvas when selected.

### Cards & Data Tiles
- Built with `#FFFFFF` surfaces, 16px to 20px rounded corners, subtle `#E5E7EB` borders, and diffused biophilic ambient shadows.
- Active or highlighted cards (such as "Today's Nutrition Target") utilize a top-accent border or subtle gradient wash of `#ECFDF5` to `#FFFFFF`.

### Metric Progress Rings & Activity Indicators
- Circular macro graphs use a neutral track `#E5E7EB` with rounded stroke caps in `#059669`, `#34D399`, and `#F59E0B`.
- Live status indicators utilize an emerald dot with a concentric, pulsing translucent halo (`rgba(16, 185, 129, 0.25)`).