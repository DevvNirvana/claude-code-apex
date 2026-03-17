#!/usr/bin/env python3
"""
Design System Generator
Produces complete design system: palette, typography, tokens, CSS variables.
Saves to design-system/MASTER.md for persistent use across sessions.

Usage:
  python3 design_system.py --product "job board" --style "professional minimal" [--dark] [--persist]
  python3 design_system.py --product "AI startup" --style "dark gradient aurora" --dark --persist
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

# Add scripts dir to path so we can import core
sys.path.insert(0, str(Path(__file__).parent))
from core import resolve_product, search_ux_laws, get_pattern, UX_LAWS


def generate(product: str, style: str, dark_mode: bool, persist: bool, page_type: str = "landing"):
    resolved = resolve_product(product, style)
    palette  = resolved["palette"]
    typo     = resolved["typography"]
    sty      = resolved["style"]
    pattern  = get_pattern(page_type)

    # UX laws most relevant to the design
    ux_laws = search_ux_laws(f"{product} {style} layout navigation CTA", n=3)

    lines = []
    W = 62

    def box(text): return f"  {text}"
    def div(label=""): return f"  {'─' * 4} {label} {'─' * max(1, W - len(label) - 6)}"

    lines.append("╔" + "═" * W + "╗")
    pname = f"{product.upper()} DESIGN SYSTEM"
    lines.append("║  " + pname.center(W - 2) + "  ║")
    lines.append("╚" + "═" * W + "╝")
    lines.append("")

    lines.append(div("PALETTE"))
    lines.append(box(f"Name:       {palette['name']}"))
    lines.append(box(f"Primary:    {palette['primary']}"))
    lines.append(box(f"Secondary:  {palette['secondary']}"))
    lines.append(box(f"CTA/Accent: {palette['cta']}"))
    lines.append(box(f"Background: {palette['bg']}"))
    if dark_mode:
        lines.append(box(f"BG Dark:    {palette['bg_dark']}"))
        lines.append(box(f"Surface Dk: {palette['surface_dark']}"))
        lines.append(box(f"Border Dk:  {palette['border_dark']}"))
    lines.append(box(f"Text:       {palette['text']}"))
    lines.append(box(f"Muted:      {palette['muted']}"))
    lines.append(box(f"Border:     {palette['border']}"))
    lines.append("")

    lines.append(div("TYPOGRAPHY"))
    lines.append(box(f"Heading:    {typo['heading']}  ({typo['weights_h']})"))
    lines.append(box(f"Body:       {typo['body']}  ({typo['weights_b']})"))
    lines.append(box(f"URL:        {typo['url']}"))
    lines.append("")

    lines.append(div("TYPE SCALE"))
    lines.append(box("display: 72px / 4.5rem  / leading-none   / font-heading"))
    lines.append(box("h1:      56px / 3.5rem  / leading-tight  / font-heading"))
    lines.append(box("h2:      40px / 2.5rem  / leading-tight  / font-heading"))
    lines.append(box("h3:      28px / 1.75rem / leading-snug   / font-heading"))
    lines.append(box("h4:      22px / 1.375rem/ leading-snug   / font-body w-600"))
    lines.append(box("body-lg: 18px / 1.125rem/ leading-relaxed/ font-body"))
    lines.append(box("body:    16px / 1rem    / leading-relaxed/ font-body"))
    lines.append(box("small:   14px / 0.875rem/ leading-normal / font-body"))
    lines.append(box("caption: 12px / 0.75rem / leading-normal / font-body"))
    lines.append("")

    lines.append(div("STYLE"))
    lines.append(box(f"Style:      {sty['name']}"))
    lines.append(box(f"Effects:    {sty['effects']}"))
    react_bits = ", ".join(sty.get('react_bits', []))
    lines.append(box(f"React Bits: {react_bits}"))
    lines.append(box(f"Avoid:      {sty['anti_patterns']}"))
    lines.append("")

    lines.append(div("ANIMATION TOKENS"))
    lines.append(box("fast:     150ms ease-out      ← hover states, micro interactions"))
    lines.append(box("normal:   250ms ease-out      ← transitions, show/hide"))
    lines.append(box("slow:     400ms ease-in-out   ← page entrances, reveals"))
    lines.append(box("spring:   600ms cubic-bezier(0.16, 1, 0.3, 1)  ← bouncy enter"))
    lines.append(box("stagger:  50ms delay between list items"))
    lines.append("")

    lines.append(div("PAGE PATTERN"))
    lines.append(box(f"Type:    {pattern['name']}"))
    for i, s in enumerate(pattern['sections'], 1):
        lines.append(box(f"  {i:2}. {s}"))
    lines.append(box(f"CTA:     {pattern['cta_placement']}"))
    lines.append(box(f"Note:    {pattern['conversion']}"))
    lines.append("")

    if ux_laws:
        lines.append(div("PSYCHOLOGY LAWS TO APPLY"))
        for law in ux_laws:
            lines.append(box(f"[{law['law']}]"))
            lines.append(box(f"  → {law['apply']}"))
        lines.append("")

    lines.append(div("CSS VARIABLES  (→ globals.css)"))
    lines.append(box(":root {"))
    lines.append(box(f"  --color-primary:   {palette['primary']};"))
    lines.append(box(f"  --color-secondary: {palette['secondary']};"))
    lines.append(box(f"  --color-cta:       {palette['cta']};"))
    lines.append(box(f"  --color-bg:        {palette['bg']};"))
    lines.append(box(f"  --color-surface:   {palette.get('surface', '#FFFFFF')};"))
    lines.append(box(f"  --color-text:      {palette['text']};"))
    lines.append(box(f"  --color-muted:     {palette['muted']};"))
    lines.append(box(f"  --color-border:    {palette['border']};"))
    lines.append(box(f"  --font-heading:    '{typo['heading']}', sans-serif;"))
    lines.append(box(f"  --font-body:       '{typo['body']}', sans-serif;"))
    lines.append(box("}"))
    if dark_mode:
        lines.append(box(".dark {"))
        lines.append(box(f"  --color-bg:      {palette['bg_dark']};"))
        lines.append(box(f"  --color-surface: {palette['surface_dark']};"))
        lines.append(box(f"  --color-text:    #F8FAFC;"))
        lines.append(box(f"  --color-muted:   #94A3B8;"))
        lines.append(box(f"  --color-border:  {palette['border_dark']};"))
        lines.append(box("}"))
    lines.append("")

    lines.append(div("FONT IMPORT"))
    lines.append(box(typo['import']))
    lines.append("")

    lines.append(div("REACT BITS INSTALL"))
    for comp in sty.get('react_bits', []):
        lines.append(box(f'npx shadcn@latest add "https://reactbits.dev/r/{comp}"'))
    lines.append("")

    lines.append(div("PRE-DELIVERY CHECKLIST"))
    checks = [
        "[ ] No emojis as icons (use SVG: Lucide / Heroicons)",
        "[ ] cursor-pointer on all clickable elements",
        "[ ] Hover transitions 150-300ms",
        "[ ] Light mode contrast 4.5:1 minimum (WCAG AA)",
        "[ ] Focus states visible for keyboard nav",
        "[ ] prefers-reduced-motion respected",
        "[ ] Responsive: 375 / 768 / 1024 / 1440px",
        "[ ] No horizontal scroll on mobile",
        "[ ] No hardcoded hex values (use CSS vars / tokens)",
        "[ ] AnimatePresence wrapping conditional Framer renders",
    ]
    for c in checks:
        lines.append(box(f"  {c}"))
    lines.append("")

    output = "\n".join(lines)
    print(output)

    if persist:
        _save_master(output, product, style, palette, typo, sty, dark_mode, pattern)

    return output


def _save_master(output, product, style, palette, typo, sty, dark_mode, pattern):
    out_dir = Path.cwd() / "design-system"
    out_dir.mkdir(exist_ok=True)
    master = out_dir / "MASTER.md"
    pages_dir = out_dir / "pages"
    pages_dir.mkdir(exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d %H:%M")

    content = f"""# Design System Master
Generated: {ts}  |  Product: {product}  |  Style: {style}

> When building a specific page, first check `design-system/pages/[page].md`.
> If that file exists, its rules override this Master.
> If not, follow this Master exclusively.

---

## Design System Output

```
{output}
```

---

## Tailwind Config Extensions

```typescript
// tailwind.config.ts
import type {{ Config }} from 'tailwindcss'

const config: Config = {{
  content: ['./src/**/*.{{ts,tsx}}', './app/**/*.{{ts,tsx}}'],
  darkMode: 'class',
  theme: {{
    extend: {{
      fontFamily: {{
        heading: ['{typo['heading']}', 'sans-serif'],
        body:    ['{typo['body']}', 'sans-serif'],
      }},
      colors: {{
        primary:   'var(--color-primary)',
        secondary: 'var(--color-secondary)',
        cta:       'var(--color-cta)',
        bg:        'var(--color-bg)',
        surface:   'var(--color-surface)',
        muted:     'var(--color-muted)',
        border:    'var(--color-border)',
      }},
      animation: {{
        'fade-in':   'fadeIn 400ms cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-up':  'slideUp 400ms cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-down':'slideDown 400ms cubic-bezier(0.16, 1, 0.3, 1)',
      }},
    }},
  }},
}}

export default config
```

---

## Page-Specific Overrides

Create `design-system/pages/[page-name].md` to override rules for specific pages.
Only document deviations from this Master.

Example pages: `landing.md`, `dashboard.md`, `auth.md`, `pricing.md`
"""

    master.write_text(content, encoding="utf-8")
    print(f"\n  ✓ Design system saved → design-system/MASTER.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--product",  "-p", default="web app")
    parser.add_argument("--style",    "-s", default="modern minimal")
    parser.add_argument("--dark",     action="store_true")
    parser.add_argument("--persist",  action="store_true")
    parser.add_argument("--page",     default="landing")
    args = parser.parse_args()

    generate(args.product, args.style, args.dark, args.persist, args.page)
