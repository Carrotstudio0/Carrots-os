# Windows-Native Development Baseline

CarrotOS is designed for native Windows development environments.

## Toolchain Direction
- C/C++: LLVM/Clang or GCC (MinGW variants) depending on component.
- Python: orchestration and manifest tooling.
- Signing and packaging utilities are integrated through Windows-native CLI tools.

## Constraints
- No WSL.
- No Docker/containers.
- No VM dependency in default contributor workflow.

## Expected Outcomes
- Deterministic artifact manifests.
- Reproducible layout assembly for bootable ISO generation.
- Clear interfaces between source assets and release artifacts.
