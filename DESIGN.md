# Veramind Design System
> LLM Reference Document — Complete design language, tokens, components, and patterns for the Veramind mindfulness & mental wellbeing platform.

---

## 1. Brand Identity

**Product:** Veramind  
**Category:** Mindfulness & Mental Wellbeing SaaS  
**Tone:** Calm, intelligent, warm, science-backed  
**Audience:** Individuals seeking stress relief, better sleep, and focus — from students to enterprise teams  

### Logo
- **Mark:** Square with `16px` border-radius, gradient fill (`#dad8f9 → #9b94e8`), single letter "V" in weight 900
- **Wordmark:** "Veramind" in Urbanist 800, color `#352b38`
- **Minimum size:** 28×28px mark, 16px wordmark

---

## 2. Typography

**Primary Font:** [Urbanist](https://fonts.google.com/specimen/Urbanist) — Google Fonts  
**Import:** `https://fonts.googleapis.com/css2?family=Urbanist:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap`  
**Fallback stack:** `'Urbanist', sans-serif`

### Type Scale

| Role | Size | Weight | Letter-spacing | Use |
|---|---|---|---|---|
| Display | 64–80px | 900 | -3px | Hero headlines |
| H1 | 48px | 800 | -2px | Page titles |
| H2 | 36px | 800 | -1.5px | Section titles |
| H3 | 24px | 700 | -0.5px | Card headers |
| H4 | 20px | 600 | 0 | Sub-headers |
| H5 | 16px | 600 | 0 | Labels |
| Body | 14–16px | 400 | 0 | Paragraphs, descriptions |
| Small | 13px | 500 | 0 | Secondary text |
| Caption | 12px | 400–600 | 0 | Hints, timestamps |
| Label | 11–12px | 700 | 0.5–1px | Uppercase section labels |

### Text Rules
- Use `text-wrap: balance` on headlines
- Use `text-wrap: pretty` on body paragraphs
- Line height: `1.05–1.1` for display, `1.3–1.4` for headings, `1.6–1.7` for body
- Gradient text: `background: linear-gradient(135deg, #352b38, #9b94e8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;`

---

## 3. Color Palette

### Core Tokens

| Token | Hex | Usage |
|---|---|---|
| `--plum` | `#352b38` | Primary text, dark backgrounds, nav |
| `--slate` | `#7e808c` | Secondary text, icons, hints |
| `--lavender` | `#dad8f9` | Primary accent, borders, card tints |
| `--ghost` | `#f4f3f8` | Page background alternative, topbars |
| `--lavender-deep` | `#9b94e8` | Active states, progress fills, links |
| `--lavender-mid` | `#b8b4f0` | Hover borders, mid-accent |
| `--lavender-soft` | `#eceaf9` | Subtle backgrounds, tab inactive, chip default |
| `--bg` | `#edeaf4` | Main app background |
| `--white` | `#ffffff` | Cards, modals, inputs |

### Semantic / Contextual Colors

| Name | Hex | Background | Use |
|---|---|---|---|
| Success | `#059669` | `#d1fae5` | Completed, positive, active |
| Danger | `#dc2626` | `#fee2e2` | Errors, destructive, urgent |
| Warning | `#92400e` | `#fef9c3` | Cautions, pending |
| Info | `#1d4ed8` | `#dbeafe` | Informational states |
| Pink (soft) | `#9d174d` | `#f9d8f0` | Featured, mood, highlight |
| Green (soft) | `#059669` | `#d8f9e8` | Growth, streaks, wellness |
| Blue (soft) | `#1e40af` | `#d8edf9` | Focus, cognitive, data |
| Peach | — | `#f9e4d8` | Warmth, onboarding |

### Gradient Recipes

```css
/* Hero background */
background: linear-gradient(160deg, #f4f3f8 0%, #edeaf4 35%, #e4e1f5 65%, #dbd6f5 100%);

/* CTA / dark section */
background: linear-gradient(135deg, #352b38 0%, #4a3550 100%);

/* Mobile app background */
background: linear-gradient(160deg, #fdeef8, #ede9fd, #e8d9fb);

/* Progress / chart fill */
background: linear-gradient(90deg, #9b94e8, #b8b4f0);

/* Stat card: lavender */
background: linear-gradient(135deg, #dad8f9 0%, #eceaf9 100%);

/* Stat card: pink */
background: linear-gradient(135deg, #f9d8f0 0%, #fde8f9 100%);

/* Stat card: blue */
background: linear-gradient(135deg, #d8edf9 0%, #e8f4fd 100%);

/* Stat card: green */
background: linear-gradient(135deg, #d8f9e8 0%, #e8fdf0 100%);

/* AI container */
background: linear-gradient(135deg, #f0effe 0%, #e8eafd 50%, #f5d8f9 100%);
```

---

## 4. Spacing & Layout

### Spacing Scale (base-4)
```
4px   — xs    (tight gaps, icon padding)
8px   — sm    (component internal)
12px  — md    (list items, form groups)
16px  — lg    (card padding tight)
20px  — xl    (card padding standard)
24px  — 2xl   (section sub-gaps)
28px  — 3xl   (modal padding)
32px  — 4xl   (topbar padding, page padding)
48px  — 5xl   (section horizontal padding)
64px  — 6xl   (section vertical padding)
96px  — 7xl   (large section vertical padding)
```

### Border Radius Scale
```
6px   — xs    (skeleton, small elements)
8px   — sm    (buttons small, chips)
10px  — md    (buttons medium, inputs)
12px  — lg    (cards tight, dropdowns)
14px  — xl    (buttons large)
16px  — 2xl   (cards standard)   ← --radius
20px  — 3xl   (large cards)
24px  — 4xl   (modals, pricing)  ← --radius-lg
28px  — 5xl   (CTA section)
32px  — phone (phone frames)
99px  — pill  (badges, toggles, pills)
```

### Shadows
```css
--shadow:    0 4px 24px rgba(53,43,56,0.07);   /* cards */
--shadow-md: 0 8px 32px rgba(53,43,56,0.10);   /* elevated cards */
/* modals */  0 20px 60px rgba(53,43,56,0.18);
/* preview */ 0 32px 80px rgba(53,43,56,0.16), 0 2px 8px rgba(53,43,56,0.06);
```

### Layout Grid
- **App shell:** Fixed 220px sidebar + fluid main content
- **Page body:** `padding: 32px`, `display: flex; flex-direction: column; gap: 48px`
- **Topbar:** `position: sticky; top: 0; height: ~64px; backdrop-filter: blur(12px)`
- **Content grids:** 2-col, 3-col, 4-col using CSS Grid with `gap: 16–20px`
- **Max content width:** 1200px centered

---

## 5. Components

### 5.1 Sidebar Navigation
```
Width: 220px, fixed, full height
Background: white
Border-right: 1px solid #eceaf9
Logo area: padding 0 20px 28px, border-bottom
Nav items: padding 9px 12px, border-radius 10px
  - Default: color #7e808c
  - Hover: background #eceaf9, color #352b38
  - Active: background #dad8f9, color #352b38, font-weight 600
Nav badges: background #9b94e8, color white, border-radius 99px, font-size 10px
Section labels: 10px, weight 600, uppercase, letter-spacing 0.8px, color #7e808c
```

### 5.2 Topbar
```
Sticky top, z-index 90
Background: rgba(244,243,248,0.85), backdrop-filter blur(12px)
Border-bottom: 1px solid #eceaf9
Search bar: white bg, border 1.5px #dad8f9, border-radius 12px, padding 8px 14px
Icon buttons: 36×36px, border-radius 10px, border 1.5px #dad8f9
Avatar: 36×36px, border-radius 50%, gradient fill
```

### 5.3 Buttons

| Variant | Background | Color | Hover |
|---|---|---|---|
| Primary | `#352b38` | white | `#4a3550` + shadow |
| Secondary | `#dad8f9` | `#352b38` | `#b8b4f0` |
| Ghost | transparent | `#352b38` | `#eceaf9` bg |
| Danger | `#fee2e2` | `#dc2626` | `#fecaca` |
| Success | `#d1fae5` | `#059669` | `#a7f3d0` |
| Icon | `#eceaf9` | `#352b38` | `#dad8f9` |
| Dark CTA | `#352b38` | white | `#4a3550` + shadow |

**Sizes:**
- `sm`: padding `6px 14px`, font `13px`, radius `8px`
- `md`: padding `10px 20px`, font `14px`, radius `10px`
- `lg`: padding `13px 28px`, font `16px`, radius `12px`
- `xl`: padding `16px 36px`, font `18px`, radius `14px`
- `pill`: `border-radius: 99px` on any size

**Hover transitions:** `translateY(-1px)` + box-shadow on primary/dark

### 5.4 Badges

| Variant | BG | Color |
|---|---|---|
| lavender | `#dad8f9` | `#352b38` |
| plum | `#352b38` | white |
| green | `#d1fae5` | `#059669` |
| red | `#fee2e2` | `#dc2626` |
| yellow | `#fef9c3` | `#92400e` |
| blue | `#dbeafe` | `#1d4ed8` |
| pink | `#f9d8f0` | `#9d174d` |
| outline | transparent | `#352b38`, border `1.5px #dad8f9` |

**Base styles:** `font-size 11px`, `font-weight 700`, `padding 3px 10px`, `border-radius 99px`

### 5.5 Inputs
```
Base: font Urbanist 14px, background white, border 1.5px #dad8f9, border-radius 10px
Padding: 10px 14px
Focus: border-color #9b94e8, box-shadow 0 0 0 3px rgba(155,148,232,0.15)
Error: border-color #dc2626
Success: border-color #059669
Disabled: opacity 0.5, cursor not-allowed
Textarea: min-height 80px, resize vertical
Select: appearance none
```

### 5.6 Toggle (Switch)
```
Width: 44px, height: 24px, border-radius 99px
Off state: background #dad8f9
On state: background #9b94e8
Knob: 18×18px white circle, box-shadow, transition transform 0.2s
On offset: translateX(20px)
```

### 5.7 Checkbox
```
18×18px, border-radius 5px
Unchecked: border 2px #b8b4f0, background white
Checked: background #9b94e8, border-color #9b94e8, checkmark content '✓'
```

### 5.8 Radio
```
18×18px, border-radius 50%
Unchecked: border 2px #b8b4f0, background white
Checked: border-color #9b94e8, inner dot 8px #9b94e8
```

### 5.9 Tabs
```
Container: background #eceaf9, border-radius 12px, padding 4px, display flex, gap 4px
Tab item: padding 8px 16px, border-radius 9px, font-size 13px, weight 600
Inactive: color #7e808c
Active: background white, color #352b38, box-shadow 0 2px 8px rgba(53,43,56,0.08)
```

### 5.10 Accordion
```
Item: border-radius 12px, background white, overflow hidden, margin-bottom 8px
Header: padding 16px 20px, font-weight 600, font-size 14px, cursor pointer
Header hover: background #eceaf9
Body: padding 0 20px 16px, font-size 14px, color #7e808c, line-height 1.6
Icon: chevron ⌄, rotates 180deg when open (transition 0.2s)
```

### 5.11 Cards

**Base card:**
```css
background: white;
border-radius: 16px;
box-shadow: 0 4px 24px rgba(53,43,56,0.07);
padding: 20px;
```

**Stat card variants:** lavender / pink / blue / green — gradient backgrounds (see Color section)  
**Feature card (landing):** border-radius 20px, border `1px solid rgba(218,216,249,0.4)`, hover `translateY(-4px)`  
**AI container:** gradient bg + before pseudo-orb, border `1px solid #dad8f9`

### 5.12 Alerts

| Type | Background | Border-left | Text |
|---|---|---|---|
| Info | `#eff6ff` | `#3b82f6` | `#1e40af` |
| Success | `#f0fdf4` | `#22c55e` | `#166534` |
| Warning | `#fffbeb` | `#f59e0b` | `#92400e` |
| Error | `#fef2f2` | `#ef4444` | `#991b1b` |

```
Layout: flex, gap 12px, padding 14px 16px, border-radius 12px, border-left 4px solid
Icon: font-size 18px, flex-shrink 0
Title: font-weight 700, font-size 14px
Desc: font-size 13px, opacity 0.85
```

### 5.13 Data Table
```
Border-collapse: separate, border-spacing 0
TH: font-size 11px, weight 700, uppercase, letter-spacing 0.5px, color #7e808c
    background #eceaf9, padding 10px 14px
    First/last TH: rounded corners 10px
TD: padding 12px 14px, font-size 13.5px, border-bottom 1px solid #eceaf9
TR hover: background #f4f3f8
```

### 5.14 Pipeline Table (colored grid)
```
Cells: border-radius 8px, padding 10px 16px, font-weight 700, font-size 15px
Color per row:
  Row 1 (Anxiety/Blue):   #dbeafe, #eff6ff, #dbeafe, #bfdbfe, #e0f2fe
  Row 2 (Sleep/Green):    #d8f9e8, #d1fae5, #d8f9e8
  Row 3 (Focus/Pink):     #f9d8f0, #fce7f3, #f9d8f0, #fbcfe8
  Row 4 (Stress/Blue-lt): #d8edf9, #dbeafe, #bfdbfe, #d8edf9, #bfdbfe
  Row 5 (Emotion/Lavndr): #dad8f9, #e0e7ff, #dad8f9, #c7d2fe
```

### 5.15 Progress Bar
```
Track: height 6px, background #eceaf9, border-radius 99px, overflow hidden
Fill (default): gradient 90deg #9b94e8 → #b8b4f0
Fill (green): gradient 90deg #34d399 → #6ee7b7
Fill (pink): gradient 90deg #f472b6 → #ec4899
```

### 5.16 Pagination
```
Buttons: 32×32px, border-radius 8px, font-size 13px, weight 600
Default: background white, color #7e808c
Active: background #9b94e8, color white, border-color #9b94e8
Hover: background #eceaf9, color #352b38
```

### 5.17 Modal
```
Overlay: rgba(53,43,56,0.35), backdrop-filter blur(4px)
Modal box: white, border-radius 24px, padding 28px, max-width 420px
Shadow: 0 20px 60px rgba(53,43,56,0.18)
Title: 20px weight 700
Body: 14px color #7e808c, line-height 1.6, margin-bottom 20px
Actions: flex, gap 10px, justify-content flex-end
```

### 5.18 Dropdown
```
Menu: white bg, border-radius 12px, shadow 0 8px 32px rgba(53,43,56,0.12)
Border: 1px solid #eceaf9, padding 6px, min-width 180px
Item: padding 8px 12px, border-radius 8px, font-size 13.5px
Item hover: background #eceaf9
Divider: height 1px, background #eceaf9, margin 4px 0
```

### 5.19 Tooltip
```
Bubble: background #352b38, color white, font-size 12px, padding 6px 12px
Border-radius: 8px, white-space nowrap
Arrow: CSS border-trick pointing downward
Trigger: :hover on parent .tooltip-wrap
Transition: opacity 0.15s
```

### 5.20 Tags & Chips
```
Tag: font-size 12px, weight 500, padding 4px 10px, border-radius 99px
     background #eceaf9, color #352b38
     Remove button: opacity 0.6, hover 1.0

Chip: padding 6px 14px, border-radius 99px, font-size 13px, weight 500
      Default: background #eceaf9, color #352b38, border 1.5px transparent
      Hover: border-color #b8b4f0
      Active: background #dad8f9, border-color #9b94e8, weight 600
```

### 5.21 Console / Workbench
```
Console bg: #352b38 (plum)
Font: 'Courier New', monospace, font-size 12px, line-height 1.8
Line colors:
  prompt:  #b8b4f0 (lavender-mid)
  success: #6ee7b7 (green)
  error:   #fca5a5 (red)
  info:    #93c5fd (blue)
  default: #a89db0 (muted)

Workbench toolbar: background #eceaf9, border-bottom 1px #dad8f9, padding 12px 16px
```

### 5.22 AI Container
```
Background: gradient 135deg #f0effe → #e8eafd → #f5d8f9
Border: 1px solid #dad8f9, border-radius 24px, padding 24px
Decorative orb: ::before pseudo, radial-gradient at top-right
AI label badge: white bg, border-radius 99px, color #9b94e8, weight 700, uppercase 11px
AI input bar: white, border 1.5px #dad8f9, border-radius 14px, overflow hidden
Send button: 36×36px, background #352b38, border-radius 10px
```

### 5.23 Quiz Component
```
Container: white card, border-radius 24px, padding 24px, shadow --shadow
Header: flex space-between — badge + progress text
Progress bar: below header, margin-bottom 20px
Question: font-size 18px, weight 700, line-height 1.4, margin-bottom 20px
Option: padding 14px 16px, border-radius 12px, border 2px #dad8f9, font-size 14px
  Hover: border-color #9b94e8, bg #eceaf9
  Selected: border #9b94e8, bg #eceaf9, weight 600
  Correct: border #059669, bg #d1fae5, color #065f46
  Wrong: border #dc2626, bg #fee2e2, color #991b1b
Option letter badge: 28×28px, border-radius 8px, bg #eceaf9, color #9b94e8
  Selected: bg #9b94e8, color white
```

### 5.24 Mood Selector
```
Button: flex column, align center, padding 12px 16px, border-radius 14px
        border 2px #eceaf9, background white
Hover: border #b8b4f0, transform scale(1.05)
Active: border #9b94e8, bg #eceaf9
Emoji: font-size 24px
Label: font-size 11px, weight 600, color #7e808c
```

### 5.25 Mini Calendar
```
Grid: 7 columns, gap 4px
Day names: 11px, weight 700, color #7e808c, center aligned
Day cells: 13px, padding 6px 4px, border-radius 8px
  Hover: bg #eceaf9
  Today: bg #9b94e8, color white, weight 700
  Has event: ::after dot 4px #9b94e8 (white if today)
  Other month: color #b8b4f0
```

### 5.26 Heatmap
```
Grid: 7 columns, gap 4px
Cells: aspect-ratio 1, border-radius 4px
  heat-0: #eceaf9
  heat-1: #c4bff7
  heat-2: #a89bf2
  heat-3: #9b94e8
  heat-4: #7065d4
```

### 5.27 Skeleton Loading
```
Background: linear-gradient(90deg, #eceaf9 25%, #dad8f9 50%, #eceaf9 75%)
Background-size: 800px 100%
Animation: shimmer 1.5s infinite (translateX from -400px to +400px)
Border-radius: 6px (default), match the shape of the element
```

---

## 6. Charts & Data Visualization

### Bar Chart
- Bars: flex column, `align-items: flex-end`, `gap: 6px`, `height: 80px`
- Bar fill: `border-radius: 6px 6px 0 0`, lavender gradient or soft lavender bg
- Active/highlighted bar: `linear-gradient(180deg, #9b94e8, #dad8f9)`
- Axis labels: 11px, color `#7e808c`, centered under each bar

### Mini Bar Chart (in stat cards)
- Height: 40–80px, bar width flexible
- Colors: `rgba(155,148,232,0.4)` default, gradient for highlighted

### Donut Chart
- SVG-based, stroke circles
- Thickness: 18–20px
- Segments: `strokeLinecap: round`, rotated -90deg from center
- Center label: absolute positioned, font-size 20px weight 800

### Line / Sparkline
- SVG polyline, stroke `#9b94e8`, strokeWidth 2.5, `strokeLinecap: round`
- Area fill: same color at 10% opacity
- No axes for sparklines; full axes for detailed views

### Radial KPI Ring
- SVG circle, `stroke-dasharray`, `stroke-dashoffset`, rotate -90deg
- Track: `#eceaf9`, fill: colored per metric
- Center text: percentage, font-size 14px weight 800

### Platform Insight Bars
- Horizontal bars, height 5px, track `#eceaf9`
- Fill: gradient from metric color to 50% opacity
- Row: icon (28×28 rounded) + name + bar + percentage

---

## 7. Animations & Transitions

### Standard Transitions
```css
transition: all 0.15s;     /* hover states, quick feedback */
transition: all 0.18s;     /* buttons, nav items */
transition: all 0.2s;      /* cards, feature cards */
transition: all 0.3s;      /* navbar scroll effect */
```

### Keyframe Animations
```css
/* Float — for hero decorative elements */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-12px); }
}
.float   { animation: float 6s ease-in-out infinite; }
.float-2 { animation: float 8s ease-in-out infinite; animation-delay: -2s; }

/* Fade up — for hero content stagger */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
.fade-up    { animation: fadeUp 0.6s ease both; }
.fade-up-d1 { animation: fadeUp 0.6s 0.1s ease both; }
.fade-up-d2 { animation: fadeUp 0.6s 0.2s ease both; }
.fade-up-d3 { animation: fadeUp 0.6s 0.3s ease both; }

/* Skeleton shimmer */
@keyframes shimmer {
  0%   { background-position: -400px 0; }
  100% { background-position:  400px 0; }
}
```

### Hover Lift Pattern
```css
/* Cards */
card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(53,43,56,0.12); }

/* Buttons */
btn:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(53,43,56,0.22); }
btn-hero:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(53,43,56,0.28); }
```

---

## 8. Page Layouts

### Dashboard (App)
```
Shell: flex row, full viewport height
Sidebar: 220px fixed, full height
Main: margin-left 220px, flex column
Topbar: sticky top 0, ~64px, blur backdrop
Page body: padding 32px, flex column, gap 48px
```

### Dashboard Content Structure
```
1. Breadcrumb / page label
2. Stat cards row (3–4 col grid)
3. Charts row (2–3 col grid)
4. Pipeline / data table
5. List panels + side widgets (2 col)
6. Timeline + Calendar (2 col)
```

### Landing Page
```
1. Navbar (fixed, glassmorphic)
2. Hero (full-viewport, centered content + dashboard preview below)
3. Features (3-col grid + stats row)
4. How It Works (white bg, 4-step horizontal)
5. Mobile Section (split: text left, phone frames right)
6. Testimonials (3-col grid)
7. Pricing (3-col, featured center card)
8. CTA (dark gradient banner)
9. Footer (4-col: brand + 3 link cols)
```

### Section Pattern (landing)
```
Padding: 96px 48px
Max-width: 1200px, centered
Section label: pill badge, font-size 12px uppercase, color #9b94e8
Section title: H2, bold, letter-spacing -1.5px
Section subtitle: body, color #7e808c, max-width 540px
Content: margin-top 52px
```

---

## 9. Interactive States

### All Interactive Elements
- **Default** → defined styles above
- **Hover** → subtle background shift, translateY(-1 to -4px), border darkening
- **Focus** → `box-shadow: 0 0 0 3px rgba(155,148,232,0.15)` on inputs; visible outline on buttons
- **Active/Pressed** → translateY(0), slight bg darken
- **Disabled** → opacity 0.4–0.5, `cursor: not-allowed`
- **Loading** → skeleton shimmer or spinner

### Navigation Active State
```css
background: #dad8f9;
color: #352b38;
font-weight: 600;
```

### Form Validation States
```css
/* Success */
border-color: #059669;
helper text: color #059669, prefix ✓

/* Error */
border-color: #dc2626;
helper text: color #dc2626, prefix ✕

/* Focus */
border-color: #9b94e8;
box-shadow: 0 0 0 3px rgba(155,148,232,0.15);
```

---

## 10. Scrollbar
```css
::-webkit-scrollbar       { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #dad8f9; border-radius: 99px; }
```

---

## 11. Mobile Design Principles

Based on the ZenBlock-inspired mobile screens:
- **Background:** warm gradient (peach → lavender) for onboarding/splash; white for content screens
- **Cards:** white, border-radius 12–16px, subtle shadow
- **Bottom nav:** dark (`#352b38`) pill/rounded container, icon + label, active item highlighted in lavender
- **Primary CTA button:** full-width, `border-radius: 99px`, background `#352b38`, large font
- **Typography:** slightly larger (16px body minimum on mobile)
- **Touch targets:** minimum 44×44px for all interactive elements
- **Phone frame:** `border-radius: 32px`, white, with dark notch pill (50px wide, 6px tall)
- **Status bar:** font-size 11px, `font-weight: 700`

---

## 12. Voice & Copy Patterns

| Context | Tone | Example |
|---|---|---|
| Greeting | Warm, personal | "Good morning, Alexandra" |
| Subtext | Gentle informational | "You have 3 sessions today" |
| AI (Vera) | Empathetic, calm | "I hear you. Work anxiety is really common." |
| CTA | Inviting, not pushy | "Begin your journey →", "Start free →" |
| Error | Honest, helpful | "Session interrupted. Progress saved to 8:32." |
| Success | Celebratory, brief | "Streak achieved! Congratulations on 7 days." |
| Empty state | Encouraging | "No sessions yet. Your first is the hardest." |
| Pricing | Transparent | "No credit card required. Cancel anytime." |

---

## 13. Do / Don't

### ✅ Do
- Use Urbanist at all sizes
- Maintain the plum + lavender palette — do not introduce new base hues
- Use `gap` (flex/grid) for all spacing between siblings, never margins between inline elements
- Use `oklch()` to derive new tints/shades if needed, keeping saturation/hue consistent
- Use `text-wrap: balance` on all multi-line headings
- Keep cards white with lavender-tinted gradient backgrounds for stats
- Use lavender-deep `#9b94e8` as the single interactive accent color
- Add `transform: translateY` lift on interactive card/button hover
- Use `backdrop-filter: blur()` for sticky bars and overlays

### ❌ Don't
- Don't use Inter, Roboto, or system fonts
- Don't use heavy drop shadows or neon glows
- Don't use aggressive gradient backgrounds on full pages (subtle only)
- Don't use emoji in UI unless explicitly part of a mood/reaction component
- Don't use left-border accent containers (outdated SaaS trope)
- Don't add filler content — every element earns its place
- Don't use `margin` between flex/grid siblings — use `gap`
- Don't mix more than 2 background colors within a single page section
- Don't use font-size below 11px in any UI element

---

## 14. File Reference

| File | Description |
|---|---|
| `components.html` | Full interactive component library — all UI elements |
| `landing.html` | Veramind marketing landing page |
| `DESIGN.md` | This document — LLM design system reference |

---

*Last updated: May 2026 · Veramind Design System v1.0*
