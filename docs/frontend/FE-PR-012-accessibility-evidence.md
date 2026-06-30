# FE-PR-012 Accessibility Evidence

This document records quick checks performed for Grade R UI features added in
FE-PR-012.

Checks

- Touch target sizes: interactive controls (`Prev`, `Next`, `Play`) have inline styles setting `min-width`/`min-height` of `64px`.
- Keyboard accessibility: controls are standard `<button>` elements with `aria-label` attributes where appropriate.
- Screen reader labels: `PhonicsKaraokeText` container exposes `role="group"` and `aria-label`.
- Reduced motion: `PhonicsKaraokeText` accepts `reducedMotion` prop and disables transitions when set.

Automated tests included

- `src/__tests__/grade-r/PhonicsKaraokeText.test.tsx` — rendering and reduced-motion behavior.
- `src/__tests__/grade-r/EarconButton.test.tsx` — opt-in and play behavior (mocked).
- `src/__tests__/grade-r/grade-r-contracts.test.tsx` — touch target contract.

Manual guidance

- Ensure guardian consent flows remain external to this feature; earcons are off by default and require user interaction to opt in.
