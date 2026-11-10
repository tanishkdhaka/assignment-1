# Clarifications

## CLR-001: Stacking rule for two non-BOGO discounts
Q: If the user applies a PERCENTAGE then a FIXED_AMOUNT, what happens?
A: The second replaces the first (last-wins). This keeps the rule simple and testable.
Decision date: 2026-11-10. Reflected in AC-008.

## CLR-002: BOGO free item calculation when qty is not a multiple of buy_qty
Q: For BOGO(buy=2, get=1) with qty=5, how many are free?
A: floor(5/2) = 2 free items. Savings = 2 * unit_price.
Decision date: 2026-11-10. Reflected in AC-009.

## CLR-003: Negative total guard
Q: Can discounts make the total negative?
A: No. subtotal_after_discounts is clamped to 0.0. Reflected in AC-020.

## CLR-004: Tax on zero subtotal
Q: If subtotal_after_discounts = 0.0, is tax still charged?
A: Tax = 0.0 (10% of 0 = 0). Covered by AC-020.

## CLR-005: FIXED_AMOUNT at exact minimum
Q: If subtotal equals exactly the minimum, is the discount accepted?
A: Yes. The check is subtotal >= minimum. Reflected in AC-018.
