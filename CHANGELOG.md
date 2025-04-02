# Changelog

All notable changes to the SQLFluff Constraint Naming Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Future changes will be documented here

## [0.1.0] - 2024-05-01

### Added
- Initial release of the SQLFluff Constraint Naming Plugin
- Rule CR01: PRIMARY KEY constraints should use `pk_` prefix
- Rule CR02: FOREIGN KEY constraints should use `fk_` prefix
- Rule CR03: CHECK constraints should use `chk_` prefix
- Rule CR04: UNIQUE constraints should use `uc_` prefix
- Rule CR05: DEFAULT constraints should use `df_` prefix (only for named constraints)
- Documentation in README.md
- Configuration options for customizing constraint prefixes
- Test suite for all rules

### Fixed
- CR05 rule properly handles DEFAULT constraints only when using the CONSTRAINT keyword

[Unreleased]: https://github.com/sergeiboikov/sqlfluff-extended-pack/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/sergeiboikov/sqlfluff-extended-pack/releases/tag/v0.1.0
