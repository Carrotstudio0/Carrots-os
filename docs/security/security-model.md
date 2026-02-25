# Security Model

## Trust Chain
- UEFI secure boot validates bootloader.
- Bootloader validates kernel + initramfs signatures.
- Initramfs validates rootfs and overlay artifacts before mount.

## Runtime Controls
- Mandatory access control policy set (AppArmor by default).
- Baseline seccomp filters for sensitive services.
- Default-deny firewall profile for inbound traffic.
- Least-privilege service users and policy-mediated escalation.

## Auditability
- Boot event signatures and overlay decisions are logged.
- Security-relevant service actions emit structured logs.
