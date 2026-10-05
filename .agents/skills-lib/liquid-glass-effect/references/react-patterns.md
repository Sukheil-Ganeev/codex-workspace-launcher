# React Liquid Glass Patterns

Use these as starting points after installing `@samasante/liquid-glass`.

## Floating Toolbar

```tsx
import { Glass } from "@samasante/liquid-glass";

export function FloatingToolbar({ children }: { children: React.ReactNode }) {
  return (
    <Glass
      radius={22}
      optics={{ frost: 8, bend: 0.45, dispersion: 0.25, sheen: 0.5 }}
      style={{
        position: "fixed",
        left: "50%",
        bottom: 24,
        transform: "translateX(-50%)",
        display: "flex",
        gap: 8,
        padding: 10,
        background: "rgba(255,255,255,0.18)",
        border: "1px solid rgba(255,255,255,0.35)",
        boxShadow: "0 18px 60px rgba(0,0,0,0.22)",
        zIndex: 50,
      }}
    >
      {children}
    </Glass>
  );
}
```

## Glass Card

```tsx
import { Glass } from "@samasante/liquid-glass";

export function GlassCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Glass
      radius={18}
      optics={{ frost: 10, bend: 0.35, dispersion: 0.18 }}
      style={{
        padding: 20,
        background: "rgba(255,255,255,0.16)",
        border: "1px solid rgba(255,255,255,0.28)",
      }}
    >
      <h2>{title}</h2>
      <div>{children}</div>
    </Glass>
  );
}
```

## Static CSS Fallback For Non-React

This is only a frosted-glass fallback, not the same live-DOM refractive engine.

```css
.glass-surface {
  background: rgba(255, 255, 255, 0.18);
  border: 1px solid rgba(255, 255, 255, 0.34);
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.22);
  backdrop-filter: blur(18px) saturate(1.35);
  -webkit-backdrop-filter: blur(18px) saturate(1.35);
}
```

