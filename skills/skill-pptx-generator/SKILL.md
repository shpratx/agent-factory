SKILL.md
markdown

Save
# Skill: AI-DLC Methodology PPTX Generator

## Description
Generates professional PowerPoint presentations following the TP ICAP AI-DLC visual design system. Ensures uniform branding, layout patterns, and styling across all methodology decks — whether for customer presentations, internal workshops, or stakeholder briefings.

## Trigger
When the user asks to create a presentation about AI-DLC methodology, technical methodology decks, customer-facing AI-DLC content, or any deck that should follow the TP ICAP dark-theme design system.

## Inputs
- `topic`: The subject matter for the presentation (e.g., "AI-DLC for Acme Corp", "Phase 1: Inception Deep Dive")
- `audience`: Target audience (e.g., "CTO", "Engineering leads", "Customer workshop")
- `slide_count`: Approximate number of slides (default: 10-15)
- `sections`: Key sections/phases to cover (optional — defaults to full AI-DLC lifecycle) 

## Design System

### Dimensions
- **Format**: Widescreen 16:9
- **Slide size**: 13.333" × 7.5" (12192000 × 6858000 EMU)

### Color Palette

| Role | Hex | Usage |
|------|-----|-------|
| Dark Background | `#0D1B2A` | Odd slides (1, 3, 5...) — primary dark bg |
| Light Background | `#E0E1DD` | Even slides (2, 4, 6...) — light content bg |
| Accent Blue | `#4DA8DA` | Top bar, accent elements, subtitles on dark, highlights |
| Dark Card Fill | `#1B2838` | Card backgrounds on dark slides |
| Body Text (dark bg) | `#778DA9` | Muted body text on dark backgrounds |
| Body Text (light bg) | `#415A77` | Body text on light/white cards |
| Heading (dark bg) | `#FFFFFF` | White headings on dark backgrounds |
| Heading (light bg) | `#0D1B2A` | Dark navy headings on light backgrounds |
| Green Accent | `#81B29A` | Numbered badges, status indicators, positive |
| Coral Accent | `#E07A5F` | Warnings, important callouts, alerts |
| White | `#FFFFFF` | Card fills on light slides, text on dark |

### Background Alternation Pattern
- **Odd slides** (1, 3, 5, 7, 9, 11, 13): Dark navy `#0D1B2A`
- **Even slides** (2, 4, 6, 8, 10, 12): Light grey `#E0E1DD`
- This creates visual rhythm and prevents monotony

### Typography

| Element | Font | Size (pt) | Weight | Color |
|---------|------|-----------|--------|-------|
| Main Title (slide 1) | Trebuchet MS | 36 | Normal | `#FFFFFF` |
| Section Title (dark bg) | Trebuchet MS | 30-32 | Normal | `#FFFFFF` |
| Section Title (light bg) | Trebuchet MS | 28-30 | Normal | `#0D1B2A` |
| Subtitle (dark bg) | Calibri | 12-13 | Normal | `#778DA9` |
| Subtitle (light bg) | Calibri | 13 | Normal | `#4DA8DA` |
| Card Heading | Trebuchet MS | 12-13 | Bold | `#0D1B2A` |
| Body Text (dark) | Calibri | 11.5-12 | Normal | `#778DA9` |
| Body Text (light) | Calibri | 10.5-11 | Normal | `#415A77` |
| Footer/Key Principle | Calibri | 11-14 | Normal | `#FFFFFF` |
| Page Number | Calibri | 10 | Normal | `#778DA9` |

### Common Elements

#### Top Accent Bar
- Full-width horizontal bar at top of every slide
- Height: ~0.06" (54864 EMU)
- Fill: `#4DA8DA`
- Position: (0, 0)

#### Page Number
- Position: Bottom-right corner
- Location: (11430000, 6400800) EMU — approximately 11.17" from left, 6.25" from top
- Size: 548640 × 274320 EMU
- Font: Calibri 10pt, color `#778DA9`

#### Bottom Key Takeaway Bar
- Full-width bar near bottom of content slides
- Fill: Dark (`#1B2838` on dark slides) or accent-appropriate
- Contains summary statement in white Calibri text
- Position Y: ~5897880 EMU (bottom area)
- Width: 10881360 EMU (nearly full width)
- Height: ~502920 EMU

#### Left Accent Bar on Cards
- Thin vertical bar on left edge of content cards
- Width: ~45720 EMU (0.05")
- Fill: `#4DA8DA` (primary) or `#81B29A` (secondary)
- Full height of the card

#### Numbered Circles/Badges
- Circle shape, 457200 × 457200 EMU (0.5" × 0.5")
- Fill: `#4DA8DA`, `#81B29A`, or `#E07A5F`
- Text: Trebuchet MS, 14pt Bold, White, centered
- Content: "01", "02", "03" or single letters

#### Arrow Connectors
- Character `▶` in Calibri
- Color: `#4DA8DA`
- Used between flow steps

## Layout Patterns

### 1. Title Slide (Slide 1 — Dark Background)
```
┌─────────────────────────────────────────────────┐
│ ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀  (top bar)   │
│                                                 │
│  │ Main Title (36pt Trebuchet, White)           │
│  │                                    ┌──────┐  │
│    Subtitle (22pt Calibri, #4DA8DA)   │ deco │  │
│                                       └──────┘  │
│    Description (14pt Calibri, #778DA9) ┌─────┐  │
│                                        │deco │  │
│    Logos / Attribution (13pt, #778DA9)  └─────┘  │
│                                                 │
│                                            [1]  │
└─────────────────────────────────────────────────┘
```

### 2. Problem / Grid Cards (Light Background)
```
┌─────────────────────────────────────────────────┐
│ ▀▀▀  (top bar)                                  │
│  Title (28pt Trebuchet, #0D1B2A)                │
│  Subtitle (13pt Calibri, #415A77)               │
│                                                 │
│  ┌│Card 1──┐  ┌│Card 2──┐  ┌│Card 3──┐  ┌│4─┐ │
│  │ Heading │  │ Heading │  │ Heading │  │ H  │ │
│  │ Body    │  │ Body    │  │ Body    │  │ B  │ │
│  └─────────┘  └─────────┘  └─────────┘  └───┘ │
│  ┌│Card 5──┐  ┌│Card 6──┐  ┌│Card 7──┐  ┌│8─┐ │
│  │ Heading │  │ Heading │  │ Heading │  │ H  │ │
│  │ Body    │  │ Body    │  │ Body    │  │ B  │ │
│  └─────────┘  └─────────┘  └─────────┘  └───┘ │
│  ▓▓▓▓▓▓▓▓▓▓▓▓ Key Takeaway Bar ▓▓▓▓▓▓▓▓▓▓▓▓  │
│                                            [2]  │
└─────────────────────────────────────────────────┘
```
- 4×2 grid (or 3×2, 2×2 depending on content)
- Each card: white fill, left accent bar (#4DA8DA)
- Card heading: Trebuchet MS 12pt Bold, #0D1B2A
- Card body: Calibri 10.5pt, #415A77

### 3. Framework / Phases Overview (Dark Background)
```
┌─────────────────────────────────────────────────┐
│ ▀▀▀  (top bar)                                  │
│  Title (32pt Trebuchet, White)                  │
│  Subtitle (12pt Calibri, #778DA9)               │
│                                                 │
│  ┌──────────┐  ▶  ┌──────────┐  ▶  ┌────────┐ │
│  │(01) Phase│     │(02) Phase│     │(03)    │  │
│  │  Name    │     │  Name    │     │ Phase  │  │
│  │  Desc    │     │  Desc    │     │  Desc  │  │
│  └──────────┘     └──────────┘     └────────┘  │
│                                                 │
│  ─── Flow Bar 1 ──────────────────────── →     │
│  ─── Flow Bar 2 ──────────────────────── →     │
│  ─── Flow Bar 3 ──────────────────────── →     │
│                                                 │
│  ▓▓▓▓▓▓▓▓ Core Principle Bar ▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │
│                                            [3]  │
└─────────────────────────────────────────────────┘
```
- 3 dark cards (#1B2838) with numbered badges
- Arrow connectors between cards
- Flow bars below with left accent dot

### 4. Two-Column Detail (Light Background)
```
┌─────────────────────────────────────────────────┐
│ ▀▀▀  (top bar)                                  │
│  Title (28pt Trebuchet, #0D1B2A)                │
│  Subtitle (13pt Calibri, #4DA8DA)               │
│                                                 │
│  ┌─── Left Column ───┐  ┌─── Right Column ──┐  │
│  │ Section box       │  │ Section header    │  │
│  │ • Bullet 1       │  │ (C) Context       │  │
│  │ • Bullet 2       │  │ (A) Action        │  │
│  │                   │  │ (S) State         │  │
│  │ Section box 2    │  │ (T) Transition    │  │
│  │ • Bullet         │  │                   │  │
│  └───────────────────┘  └───────────────────┘  │
│                                                 │
│  ▓▓▓▓▓▓▓▓ Ground Rules Bar ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │
│                                            [4]  │
└─────────────────────────────────────────────────┘
```

### 5. Process Flow (Dark Background)
```
┌─────────────────────────────────────────────────┐
│ ▀▀▀  (top bar)                                  │
│  Title (32pt Trebuchet, White)                  │
│  Subtitle (12pt Calibri, #778DA9)               │
│                                                 │
│  (1) ▶ (2) ▶ (3) ▶ (4) ▶ (5)                  │
│  Step   Step   Step   Step   Step               │
│                                                 │
│  ┌─ Output 1 ─┐ ┌─ Output 2 ─┐ ┌─ Output 3 ─┐│
│  │ desc       │ │ desc       │ │ desc       │ │
│  └────────────┘ └────────────┘ └────────────┘  │
│                                                 │
│  ▓▓ Key note / disclaimer bar ▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │
│                                            [5]  │
└─────────────────────────────────────────────────┘
```

### 6. Technical Detail / Bullets (Light or Dark)
```
┌─────────────────────────────────────────────────┐
│ ▀▀▀  (top bar)                                  │
│  Title                                          │
│  Subtitle                                       │
│                                                 │
│  ┌─ Section 1 ─────────────────────────────┐   │
│  │ (1) Component Name                       │   │
│  │     Subheading                           │   │
│  │     • Bullet point 1                     │   │
│  │     • Bullet point 2                     │   │
│  │     • Bullet point 3                     │   │
│  └──────────────────────────────────────────┘   │
│  ┌─ Section 2 ─────────────────────────────┐   │
│  │ (2) Component Name                       │   │
│  │     • Bullet point                       │   │
│  └──────────────────────────────────────────┘   │
│                                            [N]  │
└─────────────────────────────────────────────────┘
```

### 7. Closing / Principle Slide (Dark Background)
```
┌─────────────────────────────────────────────────┐
│ ▀▀▀  (top bar)                                  │
│                                                 │
│                                                 │
│         Title (Large, White, Centered)          │
│         Subtitle (Calibri, #778DA9)             │
│                                                 │
│                                                 │
│  ▓▓▓▓▓ Core Principle Statement ▓▓▓▓▓▓▓▓▓▓▓▓  │
│                                           [13]  │
└─────────────────────────────────────────────────┘
```

## Implementation Instructions

### Technology
Use `pptxgenjs` (JavaScript) for generation via Kiro's code execution. The library supports all required features: custom shapes, text formatting, solid fills, and precise positioning.

### Step-by-Step Process

1. **Gather Content**: Collect the topic, audience, and section content from the user
2. **Plan Slide Structure**: Map content to layout patterns (title → grid → overview → details → closing)
3. **Apply Background Alternation**: Odd slides dark (#0D1B2A), even slides light (#E0E1DD)
4. **Build Each Slide**:
   - Start with top accent bar
   - Add title + subtitle with correct typography
   - Apply layout pattern (grid, columns, flow, etc.)
   - Add bottom key takeaway bar where appropriate
   - Add page number bottom-right
5. **Review for Consistency**: Ensure colours, fonts, and spacing match the design system

### Code Template (pptxgenjs)

```javascript
const pptxgen = require('pptxgenjs');
const prs = new pptxgen();

// Slide dimensions
prs.defineLayout({ name: 'CUSTOM', width: 13.33, height: 7.5 });
prs.layout = 'CUSTOM';

// Color constants
const COLORS = {
  darkBg: '0D1B2A',
  lightBg: 'E0E1DD',
  accentBlue: '4DA8DA',
  darkCard: '1B2838',
  mutedText: '778DA9',
  bodyDark: '415A77',
  headingLight: 'FFFFFF',
  headingDark: '0D1B2A',
  green: '81B29A',
  coral: 'E07A5F',
  white: 'FFFFFF'
};

// Helper: Add top accent bar
function addTopBar(slide) {
  slide.addShape('rect', {
    x: 0, y: 0, w: 13.33, h: 0.06,
    fill: { color: COLORS.accentBlue },
    line: { type: 'none' }
  });
}

// Helper: Add page number
function addPageNumber(slide, num) {
  slide.addText(String(num), {
    x: 11.17, y: 6.25, w: 0.6, h: 0.3,
    fontSize: 10, fontFace: 'Calibri',
    color: COLORS.mutedText, align: 'center'
  });
}

// Helper: Add bottom key takeaway bar
function addKeyTakeaway(slide, text, isDark = true) {
  slide.addShape('rect', {
    x: 0.5, y: 5.75, w: 10.88, h: 0.5,
    fill: { color: isDark ? COLORS.darkCard : COLORS.accentBlue },
    line: { type: 'none' }, rectRadius: 0.02
  });
  slide.addText(text, {
    x: 0.65, y: 5.75, w: 10.56, h: 0.5,
    fontSize: 11, fontFace: 'Calibri',
    color: COLORS.white, valign: 'middle'
  });
}

// Helper: Dark slide with title
function createDarkSlide(title, subtitle) {
  const slide = prs.addSlide();
  slide.background = { fill: COLORS.darkBg };
  addTopBar(slide);
  slide.addText(title, {
    x: 0.5, y: 0.25, w: 8, h: 0.6,
    fontSize: 30, fontFace: 'Trebuchet MS',
    color: COLORS.headingLight, bold: false
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.5, y: 0.8, w: 8, h: 0.35,
      fontSize: 12, fontFace: 'Calibri',
      color: COLORS.mutedText
    });
  }
  return slide;
}

// Helper: Light slide with title
function createLightSlide(title, subtitle) {
  const slide = prs.addSlide();
  slide.background = { fill: COLORS.lightBg };
  addTopBar(slide);
  slide.addText(title, {
    x: 0.5, y: 0.25, w: 8, h: 0.55,
    fontSize: 28, fontFace: 'Trebuchet MS',
    color: COLORS.headingDark, bold: false
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.5, y: 0.75, w: 8, h: 0.3,
      fontSize: 13, fontFace: 'Calibri',
      color: COLORS.accentBlue
    });
  }
  return slide;
}

// Helper: Add card with left accent bar (for light slides)
function addCard(slide, x, y, w, h, heading, body, accentColor = COLORS.accentBlue) {
  // Card background
  slide.addShape('rect', {
    x, y, w, h,
    fill: { color: COLORS.white },
    line: { type: 'none' }, rectRadius: 0.02
  });
  // Left accent bar
  slide.addShape('rect', {
    x, y: y + 0.05, w: 0.04, h: h - 0.1,
    fill: { color: accentColor },
    line: { type: 'none' }
  });
  // Heading
  slide.addText(heading, {
    x: x + 0.15, y: y + 0.05, w: w - 0.3, h: 0.35,
    fontSize: 12, fontFace: 'Trebuchet MS',
    color: COLORS.headingDark, bold: true
  });
  // Body
  slide.addText(body, {
    x: x + 0.15, y: y + 0.4, w: w - 0.3, h: h - 0.5,
    fontSize: 10.5, fontFace: 'Calibri',
    color: COLORS.bodyDark, valign: 'top'
  });
}

// Helper: Numbered badge
function addBadge(slide, x, y, number, color = COLORS.accentBlue) {
  slide.addShape('ellipse', {
    x, y, w: 0.45, h: 0.45,
    fill: { color },
    line: { type: 'none' }
  });
  slide.addText(String(number).padStart(2, '0'), {
    x, y, w: 0.45, h: 0.45,
    fontSize: 14, fontFace: 'Trebuchet MS',
    color: COLORS.white, bold: true,
    align: 'center', valign: 'middle'
  });
}
```

## Quality Checklist
- [ ] Slide backgrounds alternate correctly (odd=dark, even=light)
- [ ] Top accent bar present on every slide
- [ ] Page numbers present bottom-right on every slide
- [ ] Headings use Trebuchet MS, body uses Calibri
- [ ] Colors match the palette exactly (no approximations)
- [ ] Cards on light slides have white fill + left accent bar
- [ ] Dark slides use #1B2838 for card backgrounds
- [ ] Bottom key takeaway bar used on content-heavy slides
- [ ] Text hierarchy is clear (title > subtitle > heading > body)
- [ ] No more than 8 cards per grid slide
- [ ] Closing slide includes core principle statement

