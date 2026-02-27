# Recent Development Updates - Quick Reference

## Overview

This document provides a quick reference for recent changes made to the HAM Agent 2.0 platform (February 26, 2026).

---

## Major Features Added

### 1. AI Assistant Persistence & Customization

**What Changed**: AI assistant now has persistent chat history and customizable system prompts

**Key Features**:

- Chat history survives page navigation (localStorage-based)
- Custom system prompts via Settings page
- Clear History button for conversation reset
- Scope-limited default prompt (Workwize data only)

**Files Modified**:

- [packages/frontend/src/app/ai-assistant/page.tsx](../packages/frontend/src/app/ai-assistant/page.tsx) - Added localStorage persistence
- [packages/backend/src/routes/ai.ts](../packages/backend/src/routes/ai.ts) - Added customPrompt support
- [packages/frontend/src/app/settings/page.tsx](../packages/frontend/src/app/settings/page.tsx) - NEW FILE (Settings page)
- [packages/frontend/src/components/Navigation.tsx](../packages/frontend/src/components/Navigation.tsx) - Added settings icon

**How to Use**:

1. Open `/settings` page (gear icon in navigation)
2. Edit system prompt in textarea
3. Click "Save Changes"
4. AI assistant will use custom prompt in all conversations

**Testing**:

```bash
# Visit settings page
http://localhost:3000/settings

# Test persistence
1. Navigate to AI Assistant
2. Ask a question
3. Navigate away and back
4. Verify chat history persists
```

---

### 2. Settings Page with Smart UX

**What Changed**: New settings page with intelligent button states

**Features**:

- Save button disabled when no changes made
- Restore Default button blue when using custom prompt
- Real-time change detection
- Default prompt preview section

**Implementation Details**:

```typescript
// State tracking
const [originalPrompt, setOriginalPrompt] = useState('');

// Computed states
const hasChanged = currentPrompt.trim() !== originalPrompt.trim();
const isNotDefault = currentPrompt.trim() !== DEFAULT_PROMPT.trim();

// Button logic
<button disabled={!hasChanged}>Save</button>
<button className={isNotDefault ? 'blue' : 'gray'}>Restore</button>
```

**Location**: `/settings`

---

### 3. Python Script Integration for Data Sync

**What Changed**: Sync page now calls Python population scripts instead of API routes

**Why**:

- More reliable than HTTP-based sync
- Better error handling and output parsing
- Consistent with original population workflow

**Files Modified**:

- [packages/backend/src/routes/sync.ts](../packages/backend/src/routes/sync.ts) - Complete rewrite
- [packages/frontend/src/app/sync/page.tsx](../packages/frontend/src/app/sync/page.tsx) - UI updates

**Key Functions**:

```typescript
// Spawn Python process
function runPythonScript(scriptPath: string): Promise<ScriptResult>;

// Parse script output
function parseScriptOutput(output: string): { count: number; entity: string };
```

**Testing**:

```bash
# Visit sync page
http://localhost:3000/sync

# Click "Populate All Data"
# Wait 5-10 minutes for completion
```

---

### 4. Scope-Limited AI System Prompt

**What Changed**: Default AI prompt now strictly enforces Workwize data scope

**Prompt Sections**:

1. **Purpose Statement**: "You are a specialized AI assistant for HAM Agent..."
2. **STRICT SCOPE LIMITATION**: Must-decline rules for out-of-scope questions
3. **AVAILABLE DATA**: Table descriptions and relationships
4. **RESPONSE GUIDELINES**: Quality standards
5. **EXAMPLE RESPONSES**: In-scope vs out-of-scope demonstrations

**Key Restrictions**:

- Can ONLY answer questions about Workwize data
- MUST decline general knowledge questions
- MUST decline programming help (unrelated to data)
- MUST decline questions about other systems

**Enforcement Language**:

```
STRICT SCOPE LIMITATION:
- You can ONLY answer questions about the Workwize data in this database
- You can ONLY query: employees, assets, products, orders, offices, warehouses, and offboards
- You MUST decline any questions outside this scope
```

**Testing**:

```bash
# Test in-scope
"How many employees are in the UK?"  # Should answer

# Test out-of-scope
"What's the weather today?"  # Should decline
"Help me write Python code"  # Should decline
```

---

## Bug Fixes

### 1. Azure OpenAI SSL Certificate Error

**Issue**: Backend crashed with `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`

**Fix**: Disabled SSL verification for development

```typescript
// packages/backend/src/lib/azure-openai.ts, Line 10
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
```

⚠️ **Note**: Re-enable for production!

---

### 2. Employee Address Country Missing

**Issue**: Assets assigned to employees showed no country (e.g., serial GY5T5C4)

**Fix**: Updated [db-build-scripts/populate_employees.py](../db-build-scripts/populate_employees.py)

- Now fetches from `/employees/{id}/addresses` endpoint
- Includes full address with country object
- Result: 1,536/1,632 employees (94%) now have addresses

**Verification**:

```sql
-- Check employee addresses
SELECT COUNT(*) FROM employees WHERE "addressId" IS NOT NULL;
-- Result: 1536

-- Check specific asset
SELECT a."serialCode", addr.country
FROM assets a
JOIN employees e ON a."assignedToId" = e.id
JOIN addresses addr ON e."addressId" = addr.id
WHERE a."serialCode" = 'GY5T5C4';
-- Result: GY5T5C4 | United Kingdom
```

---

## Repository Cleanup

### Git Configuration Updates

**Changed**: Updated [.gitignore](../.gitignore) with better patterns

**Additions**:

```gitignore
# Next.js builds
.next/
out/

# Test scripts
check_*.py
fetch_*.py
find_*.py
query_*.py
test_*.py
verify_*.py
```

**Cleanup Actions**:

- Removed 79+ tracked build artifact files
- Used `git rm --cached` for already-tracked files
- Cleaned turbo log files from tracking

**Result**: Repository size reduced, cleaner git status

---

## localStorage Schema

### Keys Used by Frontend

| Key                | Type       | Purpose                                  |
| ------------------ | ---------- | ---------------------------------------- |
| `ai-chat-history`  | JSON Array | Persistent conversation history          |
| `ai-system-prompt` | String     | Custom system prompt (overrides default) |

### Data Formats

**ai-chat-history**:

```json
[
  { "role": "user", "content": "How many employees?" },
  { "role": "assistant", "content": "There are 1,632 employees..." }
]
```

**ai-system-prompt**:

```
"You are a specialized AI assistant for the HAM Agent..."
```

---

## API Changes

### Backend Routes Modified

#### POST /api/ai/chat

**New Parameter**: `customPrompt` (optional)

**Request Body**:

```typescript
{
  message: string;
  conversationHistory: Array<{role: string, content: string}>;
  customPrompt?: string;  // NEW - overrides default system prompt
}
```

**Behavior**:

- If `customPrompt` provided, uses it instead of default
- Appends database context to system message
- Returns AI response as before

---

## Configuration Changes

### Environment Variables

No new environment variables required for AI features.

**Existing Variables** (unchanged):

```bash
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4
NODE_TLS_REJECT_UNAUTHORIZED=0  # Dev only
```

---

## Testing Checklist

### AI Assistant Features

- [ ] Chat history persists after navigation
- [ ] Clear History button works
- [ ] Custom prompts save correctly
- [ ] Settings page buttons show correct states
- [ ] Scope-limited prompt declines out-of-scope questions

### Sync Functionality

- [ ] Sync page loads without errors
- [ ] Python scripts execute successfully
- [ ] Results display correctly
- [ ] Error handling works

### Git Repository

- [ ] No untracked build artifacts in `git status`
- [ ] `.next/` folders not tracked
- [ ] Test scripts not tracked

---

## Documentation Files

### New Documentation

1. **[AI_ASSISTANT_FEATURES.md](AI_ASSISTANT_FEATURES.md)**
   - Comprehensive AI assistant documentation
   - Architecture, features, configuration
   - Troubleshooting and usage guidelines

2. **[CHANGELOG.md](CHANGELOG.md)**
   - Version history (2.0.0 → 2.0.3)
   - Breaking changes log
   - Upcoming features roadmap

3. **[RECENT_UPDATES.md](RECENT_UPDATES.md)** (This file)
   - Quick reference for recent changes
   - Testing checklist
   - Configuration summary

### Updated Documentation

1. **[INITIAL_BUILD.md](INITIAL_BUILD.md)**
   - Added AI features to documentation requirements
   - Added Azure OpenAI SSL fix section
   - Added AI success metrics

---

## Known Issues

### Remaining Problems

1. **Backend Startup**: Still requires manual intervention
   - Issue: Port conflicts not automatically resolved
   - Workaround: Manually kill Node processes, restart
   - Priority: Medium

2. **Prompt Effectiveness**: User questioning scope enforcement
   - Issue: "MUST decline" language may not be explicit enough
   - Consideration: Add stronger directives or consequence language
   - Priority: Low (prompt is functional, may need refinement)

---

## Migration Notes

### Upgrading from Previous Version

No breaking changes from 2.0.2 → 2.0.3

**Steps**:

1. Pull latest code
2. Run `npm install` (no new dependencies)
3. Restart frontend/backend
4. Test AI assistant persistence
5. Configure custom prompt if desired

**Data Migration**: Not required (database schema unchanged)

---

## Performance Impact

### localStorage Usage

- **Chat History**: ~10-50KB per conversation
- **Custom Prompt**: ~2-5KB
- **Total Impact**: Minimal (<100KB typical)

### Backend Impact

- **AI Route**: No performance change (custom prompt adds ~1KB to request)
- **Memory**: No server-side caching (stateless)
- **Sync Route**: Improved reliability with Python scripts

---

## Security Considerations

### New Security Notes

1. **localStorage Exposure**: Chat history stored client-side
   - Risk: Accessible via browser DevTools
   - Mitigation: No server-side storage, user-controlled

2. **Custom Prompt Injection**: Users can modify system prompt
   - Risk: Potential for malicious prompt instructions
   - Mitigation: Database access is read-only, Prisma prevents SQL injection
   - Recommendation: Restrict Settings page to admins (future feature)

3. **SSL Verification Disabled**: Development environment only
   - Risk: MITM attacks in dev
   - Mitigation: Production should re-enable
   - Status: Development-only setting

---

## Support

### Troubleshooting Resources

1. **AI Features**: See [AI_ASSISTANT_FEATURES.md](AI_ASSISTANT_FEATURES.md) - Troubleshooting section
2. **Build Issues**: See [INITIAL_BUILD.md](INITIAL_BUILD.md) - Common Pitfalls
3. **Version History**: See [CHANGELOG.md](CHANGELOG.md)

### Quick Fixes

**Chat history not persisting?**

- Check browser console for localStorage errors
- Verify `ai-chat-history` key exists in DevTools → Application → localStorage

**Custom prompt not working?**

- Check `ai-system-prompt` key in localStorage
- Verify Network tab shows `customPrompt` in request body

**Sync page errors?**

- Ensure Python scripts exist in `db-build-scripts/`
- Check backend console for script execution errors
- Verify database connection is active

---

## Next Steps

### Immediate Actions

1. Test all new features in browser
2. Verify chat persistence works correctly
3. Test custom prompts with various configurations
4. Commit documentation updates

### Future Enhancements

- Multi-user authentication
- Settings page access control
- Audit logging for prompt changes
- Conversation export/import
- Token usage tracking

---

**Last Updated**: February 26, 2026  
**Version**: 2.0.3  
**Status**: Stable
