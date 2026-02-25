# Overlay Model

## Layer Precedence (low -> high)
1. base
2. edition
3. oem
4. custom
5. writable upper layer

## Sources
- Static layers live under `overlays/` and are packed into release assets.
- Optional persistence upper layer may live on a dedicated USB partition.

## Security Rules
- In secure mode, unsigned overlay artifacts are rejected.
- Critical paths can be protected from override by policy.
- Overlay resolution is recorded in boot logs for diagnostics.
