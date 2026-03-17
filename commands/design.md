# /design — UI/UX Generation

You are generating **production-quality UI** for: $ARGUMENTS

---

## Step 1: Detect UI Layer Type

```bash
cat .claude/config/stack-profile.json 2>/dev/null | python3 -c "
import json, sys
try:
    p = json.load(sys.stdin)
    print('FRAMEWORK:', p.get('framework'))
    print('HAS_TAILWIND:', p.get('tailwind'))
    print('TW_VERSION:', p.get('tailwind_version'))
    print('HAS_SHADCN:', p.get('has_shadcn'))
    print('HAS_FRAMER:', p.get('has_framer'))
    print('HAS_THREE:', p.get('has_three'))
    print('LANGUAGE:', p.get('language'))
    print('PLATFORM:', p.get('platform'))
except: print('No stack profile')
"
```

**Branch based on UI layer:**
- **React/Next.js/Vue/Svelte** → Section A: Component-based UI
- **Django templates / ERB / Blade / Jinja** → Section B: Server-rendered HTML/CSS
- **Flutter** → Section C: Flutter widget tree
- **SwiftUI** → Section D: SwiftUI views
- **React Native** → Section E: React Native components
- **No UI layer detected / API-only** → explain design applies to API response shapes + error UX

---

## Step 2: Load Design Context

```bash
# Always load CLAUDE.md for project conventions + brand
cat CLAUDE.md 2>/dev/null

# Check for design system or theme files
find . -name "THEMES*" -o -name "design-tokens*" -o -name "theme.ts" \
       -o -name "colors.ts" -o -name "tailwind.config*" \
  ! -path '*/node_modules/*' 2>/dev/null | head -5 | xargs cat 2>/dev/null || true

# Check globals.css for CSS variables / design tokens
find . -name "globals.css" ! -path '*/node_modules/*' 2>/dev/null | head -1 | xargs cat 2>/dev/null | head -60 || true

# Check existing components for style patterns
find . -path '*/components/*' -name "*.tsx" -o -path '*/components/*' -name "*.vue" \
  ! -path '*/node_modules/*' 2>/dev/null | head -3 | xargs cat 2>/dev/null | head -80 || true
```

Extract: brand colors, typography scale, spacing system, design language, existing patterns.

---

## SECTION A: React / Next.js / Vue / Svelte

You are building components/pages that render in the browser with a component framework.

### Design Principles
- Mobile-first. Every layout must work at 375px before desktop.
- Accessible by default: semantic HTML, ARIA labels, keyboard navigation, 4.5:1 contrast.
- Performant: lazy loading for images, skeleton states for async, no layout shift.
- Consistent with project's design system (extract from globals.css / THEMES).

### Tailwind v3 (if detected)
```typescript
// Use project colors from globals.css --variables or CLAUDE.md brand section
// Never hardcode hex values — use semantic tokens from the design system
className="bg-background text-foreground border-border"
className="text-primary hover:text-primary/80 transition-colors"
```

### Tailwind v4 (if detected)
```css
/* Use @theme{} syntax — CSS-first configuration */
@theme {
  --color-primary: #8A2EFF;
}
/* In components: use semantic class names, not raw hex */
```

### Component Output Format
Generate complete, copy-paste-ready components:
1. TypeScript types/interfaces at the top
2. Main component with full implementation
3. Loading skeleton variant
4. Empty state variant (if list/data component)
5. Error state variant (if async)

```typescript
// Standard component structure
interface [ComponentName]Props {
  // typed props
}

export function [ComponentName]({ ...props }: [ComponentName]Props) {
  // implementation
}

export function [ComponentName]Skeleton() {
  // loading state
}

export function [ComponentName]Empty() {
  // empty state
}
```

### Animation (if Framer Motion detected)
```typescript
import { motion, AnimatePresence } from "framer-motion";

// Subtle, purposeful animation — never decorative
const fadeIn = { initial: { opacity: 0, y: 8 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.2 } };
```

---

## SECTION B: Server-Rendered Templates (Django/Rails/PHP)

You are generating HTML templates + CSS for server-rendered pages.

### Template Generation
Output complete, valid HTML templates using the project's templating language:

**Django (Jinja2):**
```html
{% extends "base.html" %}
{% block content %}
<main class="[layout]" aria-label="[page description]">
  {% if items %}
    {% for item in items %}
      <article class="[card-styles]">
        <!-- content -->
      </article>
    {% empty %}
      <div class="empty-state" role="status">No items found</div>
    {% endfor %}
  {% else %}
    <div class="empty-state" role="status">No items found</div>
  {% endif %}
</main>
{% endblock %}
```

**Rails ERB:**
```erb
<main class="[layout]" aria-label="[page description]">
  <% if @items.any? %>
    <% @items.each do |item| %>
      <%= render "item", item: item %>
    <% end %>
  <% else %>
    <%= render "shared/empty_state", message: "No items found" %>
  <% end %>
</main>
```

### CSS Output
If Tailwind is present: use utility classes.
If CSS modules: generate a `.module.css` file alongside.
If plain CSS: generate semantic class names with BEM convention.

Always include:
- `:focus-visible` styles for keyboard navigation
- Responsive breakpoints
- Dark mode support if project uses it

---

## SECTION C: Flutter Widget Tree

```dart
class [WidgetName] extends StatelessWidget {
  final [DataType] data;
  const [WidgetName]({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('[Title]')),
      body: SafeArea(
        child: [content],
      ),
    );
  }
}
```

---

## SECTION D: SwiftUI Views

```swift
struct [ViewName]: View {
  let data: [DataType]
  
  var body: some View {
    NavigationStack {
      List(data) { item in
        [ItemView](item: item)
      }
      .navigationTitle("[Title]")
    }
  }
}
```

---

## SECTION E: React Native

Use React Native core components. No web-only APIs (no CSS, no window, no document).

```typescript
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

export function [ComponentName]() {
  return (
    <SafeAreaView style={styles.container}>
      {/* implementation */}
    </SafeAreaView>
  );
}
```

---

## Step 2b: Establish Aesthetic Direction (before coding)

Before writing a line of code, define the visual direction. Avoid generic AI aesthetics:
❌ No: system fonts (Inter, -apple-system), purple gradients, rounded gray cards, center-aligned everything
✅ Yes: a specific aesthetic direction with intent

Pick ONE from: brutalist / maximalist / retro-futuristic / luxury / playful / editorial / dark-neon / minimal-swiss / raw-technical

For the chosen direction, define:
- **Typography:** specific pairing (e.g., "Syne for headings, JetBrains Mono for data")
- **Color story:** 2-3 colors with purpose (e.g., "void black base, electric violet primary, cyan accent")
- **Motion:** if animations, what character (e.g., "spring physics, overshoots, never linear")
- **Composition:** grid-breaking or strict grid, density, whitespace philosophy

State this direction before coding. The code must serve the direction, not the other way around.

## Step 3: Quality Bar

Before outputting, verify:
- [ ] Every interactive element has keyboard + screen reader support
- [ ] Loading, empty, and error states are all present
- [ ] Colors from project's design system (no hardcoded hex)
- [ ] Mobile layout works at 375px
- [ ] TypeScript types are complete (no `any`)
- [ ] Component is self-contained (imports listed, types defined)

---

> **Token Target:** ≤ 1200 output tokens per component.
> **No placeholder UI:** every component ships production-ready, not "TODO: style this".
> **Design system first:** always extract brand colors and patterns from the project before generating.
> **After outputting:** ask "Was this design on target? (y / partially: reason / n: reason)" then:
> `python3 .claude/intelligence/taste_memory.py log design [signal] "[context]" "[note]"`
