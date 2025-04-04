# Changelog

All notable changes to the SQLFluff Extended Pack project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-04-04

### Added

- Function naming rules:
  - **FN01**: Functions should use the `fun_` prefix
  - **FN02**: Function parameters should use the `p_` prefix
- View naming rules:
  - **VW01**: Views (including materialized views) should use the `v_` prefix
- Expanded test coverage for all rules
- Support for materialized views in VW01

### Changed

- Updated documentation to include function and view naming rules
- Updated configuration examples in README

## [0.1.0] - 2025-04-02

### Added

- Initial release
- Constraint naming rules:
  - **CR01**: PRIMARY KEY constraints should use the `pk_` prefix
  - **CR02**: FOREIGN KEY constraints should use the `fk_` prefix
  - **CR03**: CHECK constraints should use the `chk_` prefix
  - **CR04**: UNIQUE constraints should use the `uc_` prefix
  - **CR05**: DEFAULT constraints should use the `df_` prefix

### Fixed
- CR05 rule properly handles DEFAULT constraints only when using the CONSTRAINT keyword

[Unreleased]: https://github.com/sergeiboikov/sqlfluff-extended-pack/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sergeiboikov/sqlfluff-extended-pack/releases/tag/v0.1.0
