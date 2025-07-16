<!-- How to add changes to the changelog (template)

## Versioning conventions
Use Semantic Versioning (SemVer) in the format: MAJOR.MINOR.PATCH

- MAJOR: Breaking changes (e.g. database structure, APIs)
- MINOR: Backward-compatible new features (e.g. added model, view, endpoint)
- PATCH: Bug fixes (e.g. validation, UI glitches)

Examples:
- 1.0.0 – First stable release
- 1.1.0 – Added a new feature (e.g. SongContribution model)
- 1.1.1 – Fixed a bug (e.g. missing field validation)

## Commit link conventions
Optionally, add a link to the related **commit** or **merge commit**:

- After version heading (preferred for full branch merges):
  ## [1.2.0] – 2025-07-11 ([commit 1a2b3c4](https://github.com/your-user/your-repo/commit/1a2b3c4d))

- After each bullet point (preferred for detailed tracking):
  - Fixed validation bug ([commit 7e9c21f](https://github.com/your-user/your-repo/commit/7e9c21f))

Use only **short commit hashes** (7–8 characters).  
Prefer linking to **merge commits** if using feature branches or PRs.

## Changelog entry template

```markdown
## [version] – [release date] ([commit hash link])

### Added
- New features, models, endpoints, etc.

### Changed
- Modified behavior or structure (e.g. refactoring, renamed fields).

### Fixed
- Bug fixes and resolved issues.

### Removed
- Code or features that were deleted.

### Deprecated
- Features that will be removed in the future.

### Security
- Vulnerability fixes or security enhancements.
```

---

## Example

```markdown
## [1.3.0] – 2025-07-15 ([commit 1a2b3c4](https://github.com/your-user/your-repo/commit/1a2b3c4d))

### Added
- New model `Album`
- New API endpoint for artist search

### Changed
- Moved validation from form to model

### Fixed
- Fixed incorrect display of song title in admin
```
-->

# CHANGELOG

## [0.0.4] – 2025-07-11
### Added
- CHANGELOG.md

---

## [0.0.3] – 2025-07-10
### Added
- Set up database migrations
- Initial admin interface
- Created core models:
  - Artist ([commit 6a88600](https://github.com/Shharki/MusicLibrary/commit/6a88600308f94866caae1e2403a754ee4ead28e8))
  - Country ([commit 2c5f97a](https://github.com/Shharki/MusicLibrary/commit/2c5f97a44c55e3d216b947bc3f1e13899ee413e2))
  - Genre ([commit e1e62ca](https://github.com/Shharki/MusicLibrary/commit/e1e62ca508bcd70f3178d8466b7ffdc0a2a46553))

### Changed
- Initial project information added to `README.md`

---

## [0.0.2] – 2025-07-09 ([commit d536ac3](https://github.com/Shharki/MusicLibrary/commit/d536ac3ad7a5f94a3947ebe404b89508708efd9d))
### Added
- `requirements.txt` file
- Django project **MusicLibrary**
- `viewer` application

### Changed
- Initial project information added to `README.md`
- Additional entries added to `.gitignore`

---

## [0.0.1] – 2025-07-07 ([commit e06a26d](https://github.com/Shharki/MusicLibrary/commit/e06a26d5022919c5bc12f203c3c1844e2bf8a921))
### Added
- Initialized project repository
- Added `.gitignore`
- Added `README.md`
