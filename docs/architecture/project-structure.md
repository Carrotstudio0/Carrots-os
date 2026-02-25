# Project Structure

CarrotOS/
  boot/        Bootloader and EFI assets
  kernel/      Linux LTS config and patch policy
  firmware/    Firmware bundle manifests
  core/        Init/session/IPC/logging boundaries
  desktop/     Compositor integration and Carrot shell
  apps/        First-party system applications
  services/    System service definitions
  security/    Security policies and key references
  overlays/    Base/edition/OEM/custom layer sources
  rootfs/      Base root filesystem source tree
  build/       System and profile manifests
  iso/         Final ISO layout contracts
  packages/    Package specs and repo metadata
  toolchain/   Native Windows toolchain definitions
  tools/       Internal helper utilities
  tests/       Boot, integration, and security tests
  docs/        Architecture and development documentation
  release/     Output artifacts and checksums
