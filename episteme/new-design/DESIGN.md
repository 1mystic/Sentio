---
name: Lumina Stats
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#494552'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#7a7583'
  outline-variant: '#cac4d4'
  surface-tint: '#674bb5'
  primary: '#674bb5'
  on-primary: '#ffffff'
  primary-container: '#a78bfa'
  on-primary-container: '#3c1989'
  inverse-primary: '#cebdff'
  secondary: '#006c4b'
  on-secondary: '#ffffff'
  secondary-container: '#64f9bc'
  on-secondary-container: '#00714e'
  tertiary: '#a93349'
  on-tertiary: '#ffffff'
  tertiary-container: '#fa7084'
  on-tertiary-container: '#6e0022'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e8ddff'
  primary-fixed-dim: '#cebdff'
  on-primary-fixed: '#21005e'
  on-primary-fixed-variant: '#4f319c'
  secondary-fixed: '#68fcbf'
  secondary-fixed-dim: '#45dfa4'
  on-secondary-fixed: '#002114'
  on-secondary-fixed-variant: '#005137'
  tertiary-fixed: '#ffdadc'
  tertiary-fixed-dim: '#ffb2b9'
  on-tertiary-fixed: '#400010'
  on-tertiary-fixed-variant: '#891933'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.3'
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.2'
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1.2'
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  container-padding: 32px
  gutter: 24px
---

## Brand & Style

This design system reimagines the typically daunting world of statistics through a lens of warmth, curiosity, and high-end aesthetics. It aims to reduce cognitive load and "math anxiety" by using a "cute-sophisticated" style—merging the playfulness of modern character-driven design with the clarity of premium educational software.

The visual language is a blend of **Glassmorphism** and **Soft Minimalism**. It utilizes deep layers of transparency and backdrop blurs to create a sense of light-filled space, moving away from the "technical-dark" aesthetic of traditional data tools. The emotional response is one of safety and encouragement; it feels less like a terminal and more like a high-end, interactive gallery of ideas.

## Colors

The palette is anchored by soft, airy pastels that define large surface areas, paired with "punchy" saturated accents for interactivity and data visualization.

- **Primary (Lavender):** Used for primary actions and the "intellectual" core of the platform.
- **Secondary (Mint):** Represents progress, correctness, and success states.
- **Tertiary (Coral):** Used sparingly for highlights, critical notifications, and "Aha!" moments.
- **Neutrals:** A range of cool grays with a hint of blue to maintain a "fresh" feel, avoiding muddy or warm tones that conflict with the pastels.

Surfaces should utilize the light tinted versions (Surface Lavender/Mint) rather than pure white to create a soft, dimensional environment.

## Typography

This design system utilizes **Plus Jakarta Sans** for its friendly, geometric, and highly readable letterforms. The rounded terminals of this font reinforce the "cute" yet professional aesthetic.

Headlines should use a heavy weight (700-800) with slightly tighter letter spacing to create a distinctive, editorial look. Body text remains spacious with a generous line height (1.6) to ensure complex statistical concepts are easy to digest. Labels are used for data points and small UI micro-copy, often paired with slightly increased letter spacing for clarity.

## Layout & Spacing

The layout philosophy is based on a **Fluid Grid** with exaggerated white space to provide "breathing room" for complex data. 

- **The 8px Rhythm:** All spacing and sizing must be multiples of 8px.
- **Margins:** Large outer margins (48px+) are used to frame the content, making the platform feel like a high-end application rather than a cluttered website.
- **Sectioning:** Content is grouped in large, floating "islands" (cards) rather than being separated by lines. 
- **Density:** We prioritize "Low Density" to ensure the user never feels overwhelmed by the statistics.

## Elevation & Depth

Hierarchy is established through **translucency and soft, colored shadows** rather than high-contrast borders.

1.  **Level 0 (Base):** Subtle pastel gradients or solid light surfaces.
2.  **Level 1 (Cards):** White background with 60-80% opacity, a 40px backdrop blur, and a very soft, diffused shadow tinted with the primary lavender color.
3.  **Level 2 (Modals/Popovers):** Higher opacity white with a crisp, low-opacity 1px border in a slightly darker version of the background color to define edges.

Avoid pure black shadows; always use a desaturated version of the primary or neutral color for shadow casting.

## Shapes

The shape language is dominated by **extreme roundness**. 

- **Containers:** Main cards and content areas use a radius of 32px or greater.
- **Interactive Elements:** Buttons and tags use pill-shaped (fully rounded) ends to maximize the "friendly" feel.
- **Data Points:** Graphs and charts should avoid sharp 90-degree angles; bar charts should have rounded caps, and line graphs should use smooth splines instead of jagged connections.

## Components

- **Buttons:** Large, pill-shaped, with a subtle "squishy" feel. Use a slight scale-down transform on click (active state).
- **Glass Cards:** The primary container for information. Must include `backdrop-filter: blur(20px)` and a subtle internal glow (top-left inner shadow).
- **Progress Bubbles:** Instead of standard progress bars, use strings of circular "pearls" that fill with Mint when a module is completed.
- **Input Fields:** Oversized with 24px padding and a soft Lavender focus ring. The background should be a slightly darker tint than the card it sits on.
- **Playful Icons:** Use "thick-stroke" (2pt+) icons with rounded ends. Where possible, add a subtle two-tone color effect using the Primary and Secondary palette.
- **Data Visualizations:** All charts must use the system palette (Mint for positive, Coral for outliers, Lavender for neutral data) and feature rounded corners on every vector element.