# HAM Agent 2.0 - Changelog

## [2.0.3] - February 26, 2026

### Added

#### AI Assistant Features

- **Persistent Chat History**: Chat conversations now survive page navigation using localStorage persistence
  - Automatically loads previous conversations on mount
  - Saves after each message exchange
  - Storage key: `ai-chat-history`
  - See: [packages/frontend/src/app/ai-assistant/page.tsx](../packages/frontend/src/app/ai-assistant/page.tsx)

- **Clear History Button**: Added red "Clear History" button to AI assistant header
  - Resets conversation UI and clears localStorage
  - Retains custom system prompt settings
  - Useful for starting fresh or testing prompt changes

- **Custom System Prompt Support**: Full customization of AI assistant behavior
  - Prompts stored in localStorage (`ai-system-prompt`)
  - Sent with every chat request to backend
  - Backend accepts `customPrompt` parameter in `/api/ai/chat` route
  - See: [packages/backend/src/routes/ai.ts](../packages/backend/src/routes/ai.ts)

- **Settings Page**: New `/settings` page for AI configuration
  - Location: [packages/frontend/src/app/settings/page.tsx](../packages/frontend/src/app/settings/page.tsx)
  - Features:
    - Editable system prompt with large textarea
    - Smart button states (Save/Restore Default)
    - Tips section for prompt engineering
    - Default prompt preview
  - Accessible via gear icon in navigation

- **Settings Navigation Icon**: Added settings cog icon to top-right navigation
  - Links to `/settings` page
  - Modern settings icon design
  - See: [packages/frontend/src/components/Navigation.tsx](../packages/frontend/src/components/Navigation.tsx)

- **Scope-Limited Default Prompt**: Updated AI system prompt to enforce strict scope
  - Only answers questions about Workwize data
  - Explicitly declines out-of-scope questions
  - Includes "STRICT SCOPE LIMITATION" section
  - Provides example responses for in/out-of-scope queries
  - See: [AI_ASSISTANT_FEATURES.md](AI_ASSISTANT_FEATURES.md) for full prompt

#### Sync Page Improvements

- **Python Script Integration**: Updated sync page to call Python population scripts
  - Previously called API routes directly
  - Now spawns Python processes for data population
  - Backend route: [packages/backend/src/routes/sync.ts](../packages/backend/src/routes/sync.ts)
  - Features:
    - `runPythonScript()` function for process management
    - `parseScriptOutput()` extracts counts from Python output
    - Sequential execution of 7 population scripts
    - Enhanced error handling and status reporting

- **UI Updates**: Improved sync page descriptions and terminology
  - Changed "Sync" to "Populate" for clarity
  - Added warnings about 5-10 minute duration
  - Enhanced results display with status colors
  - Better error handling in UI
  - See: [packages/frontend/src/app/sync/page.tsx](../packages/frontend/src/app/sync/page.tsx)

#### Documentation

- **AI Assistant Features Guide**: Comprehensive documentation of AI system
  - File: [docs/AI_ASSISTANT_FEATURES.md](AI_ASSISTANT_FEATURES.md)
  - Covers: architecture, features, configuration, troubleshooting
  - Includes prompt engineering guidelines
  - Documents security considerations

- **Warehouse Location Mapping**: Created reference for warehouse physical locations
  - File: [docs/WORKWIZE_WAREHOUSE_LOCATION_MAP.md](WORKWIZE_WAREHOUSE_LOCATION_MAP.md)
  - Clarifies warehouse "country" = service region, not physical location
  - Maps warehouses to actual data center locations

- **Changelog**: This file to track version history and changes

### Fixed

#### Backend

- **Azure OpenAI SSL Certificate Error**: Resolved `UNABLE_TO_GET_ISSUER_CERT_LOCALLY` error
  - Added `process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'` for development
  - Location: [packages/backend/src/lib/azure-openai.ts](../packages/backend/src/lib/azure-openai.ts), Line 10
  - ⚠️ Development only - re-enable SSL verification for production

#### Data Population

- **Employee Address Population**: Fixed missing country data for assigned assets
  - Updated [db-build-scripts/populate_employees.py](../db-build-scripts/populate_employees.py)
  - Now fetches full address data including country from `/employees/{id}/addresses`
  - Result: 1,536/1,632 employees (94%) now have complete addresses
  - Asset serial GY5T5C4 and others now show proper country assignments

### Changed

#### Git Configuration

- **Updated .gitignore**: Improved patterns for cleaner repository
  - Added `.next/` and `out/` for Next.js build artifacts
  - Added test script patterns: `check_*.py`, `fetch_*.py`, `find_*.py`, etc.
  - Prevents tracking of temporary build outputs
  - See: [.gitignore](../.gitignore)

- **Repository Cleanup**: Removed 79+ tracked build artifact files
  - Removed `.next/` build outputs from git history
  - Removed turbo log files (`.turbo/*.log`)
  - Used `git rm --cached` to stop tracking existing artifacts
  - Repository now cleaner and faster to clone

#### UX Improvements

- **Settings Page Button States**: Implemented smart button logic
  - Save button: Disabled when no changes, blue when modified
  - Restore Default button: Blue when using custom prompt, gray when default
  - Tracks original prompt for change detection
  - Prevents accidental saves with no changes

### Data Population Results

**Final Database State**:

- **Employees**: 1,632 total
  - 1,536 with addresses (94% coverage)
  - 96 without addresses (6% - Workwize data gap)
- **Assets**: 1,699 total
  - All assets now show proper country from employee address or warehouse
- **Addresses**: 1,550 total
  - 1,536 employee addresses (with country, city, postal code)
  - 14 warehouse addresses
- **Warehouses**: 16 total (service centers with country/region mappings)
- **Offices**: 5 total

---

## [2.0.2] - February 20, 2026

### Added

- Asset pagination (100 items per page)
- Office data sample: [data-samples/offices.json](../data-samples/offices.json)

### Fixed

- Backend port conflicts (manual restart required)

---

## [2.0.1] - February 15, 2026

### Added

- Complete employee address population from Workwize API
- Parallel processing in population scripts (10 workers)
- Comprehensive API documentation

### Fixed

- Schema v2.0 migration issues
- Address field mapping (city/region/postalCode)

---

## [2.0.0] - February 10, 2026

### Added

- Complete v2.0 schema migration
- PostgreSQL database in Podman
- Next.js frontend with Tailwind CSS
- Express.js backend with Prisma ORM
- Python population scripts with ThreadPoolExecutor
- Initial AI assistant integration

### Documentation

- [INITIAL_BUILD.md](INITIAL_BUILD.md) - Project setup guide
- [SECURITY_GUIDELINES.md](SECURITY_GUIDELINES.md) - Security best practices
- [PII_SCRUBBING_GUIDELINES.md](PII_SCRUBBING_GUIDELINES.md) - Data handling
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Schema reference
- [WORKWIZE_APIS.md](WORKWIZE_APIS.md) - API documentation

---

## Version Numbering

**Format**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes, major feature releases (e.g., schema v2.0)
- **MINOR**: New features, non-breaking changes (e.g., AI assistant)
- **PATCH**: Bug fixes, documentation updates, small improvements

**Current Version**: 2.0.3

---

## Upcoming Features

### Planned for 2.0.4

- [ ] Settings page access control (admin only)
- [ ] Audit logging for system prompt changes
- [ ] Conversation export/import
- [ ] Multiple saved prompt templates
- [ ] Token usage tracking

### Planned for 2.1.0

- [ ] Advanced query builder UI for AI assistant
- [ ] Response regeneration
- [ ] Conversation branching
- [ ] Excel report export from AI queries
- [ ] Multi-user support with authentication

### Under Consideration

- [ ] Vector embeddings for semantic search
- [ ] Custom function calling for specific queries
- [ ] Scheduled report generation
- [ ] Mobile-responsive improvements
- [ ] Dark mode theme

---

## Breaking Changes

### 2.0.0 → 2.0.3

- None (backward compatible)
- localStorage keys added (non-breaking)
- API routes accept optional parameters (backward compatible)

### 1.0 → 2.0.0

- Complete database schema redesign
- Migration required from v1 schema
- See: [SCHEMA_MIGRATION_v1_to_v2.md](SCHEMA_MIGRATION_v1_to_v2.md)

---

## Contributors

- Development Team
- Azure OpenAI Integration
- Database Architecture
- Frontend/Backend Implementation

---

## License

Proprietary - Internal Use Only
