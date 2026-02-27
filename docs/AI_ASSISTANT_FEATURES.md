# AI Assistant Features Documentation

## Overview

The HAM Agent 2.0 platform includes an AI-powered assistant that provides natural language querying capabilities for the Workwize data cache. This document covers the implementation, features, and configuration of the AI assistant system.

---

## Architecture

### Components

**Frontend** (`packages/frontend/src/app/ai-assistant/`):

- Chat interface with persistent conversation history
- Real-time message streaming
- localStorage-based persistence
- Custom system prompt support

**Backend** (`packages/backend/src/routes/ai.ts`):

- Azure OpenAI integration
- Dynamic database context injection
- Custom prompt handling
- Conversation history management

**Settings** (`packages/frontend/src/app/settings/`):

- System prompt customization interface
- Save/restore functionality
- Smart button UX states

---

## Key Features

### 1. Persistent Chat History

**Implementation**: localStorage-based persistence

- Chat history survives page navigation
- Automatically loads previous conversations on mount
- Saves after each message exchange

**Technical Details**:

```typescript
// Load history on component mount
useEffect(() => {
  const savedMessages = localStorage.getItem('ai-chat-history');
  if (savedMessages) {
    setMessages(JSON.parse(savedMessages));
  }
}, []);

// Save on every message change
useEffect(() => {
  localStorage.setItem('ai-chat-history', JSON.stringify(messages));
}, [messages]);
```

**Storage Key**: `ai-chat-history`

### 2. Clear History Feature

**Location**: AI Assistant page header

- Red "Clear History" button for easy conversation reset
- Clears both UI state and localStorage
- Retains custom system prompt settings

**Use Cases**:

- Starting fresh conversation context
- Testing prompt changes
- Removing sensitive queries from history

### 3. Custom System Prompts

**Feature**: Full customization of AI assistant behavior through editable system prompts

**Storage**:

- Key: `ai-system-prompt`
- Format: Plain text string
- Sent with every chat request

**Default Prompt** (Scope-Limited):

```
You are a specialized AI assistant for the HAM Agent Workwize Management Platform.
Your ONLY purpose is to help users query and analyze data from their local Workwize
database cache.

STRICT SCOPE LIMITATION:
- You can ONLY answer questions about the Workwize data in this database
- You can ONLY query: employees, assets, products, orders, offices, warehouses, and offboards
- You MUST decline any questions outside this scope, including:
  - General knowledge questions
  - Programming help unrelated to querying this data
  - Other business systems or platforms
  - Personal advice or opinions

AVAILABLE DATA:
The database contains the following tables with relationships:
- employees: Basic employee information (name, email, start date)
- assets: Hardware assets (laptops, monitors, etc.) with assignment tracking
- products: Product catalog from Workwize
- orders: Purchase orders for hardware
- addresses: Location data for employees, warehouses, and offices
- warehouses: Workwize warehouse/service center locations
- offices: Company office locations
- offboards: Employee offboarding records

RESPONSE GUIDELINES:
- When asked about data, query the PostgreSQL database
- Provide specific answers based on actual data
- If data is incomplete or missing, state that clearly
- For complex queries, break down your analysis step-by-step
- Format responses clearly with tables, lists, or summaries as appropriate

EXAMPLE RESPONSES:

In-scope question: "How many laptops are assigned to employees in the UK?"
✓ Response: Query the database and provide the count with details.

Out-of-scope question: "What's the weather like today?"
✗ Response: "I can only help with Workwize data queries. Please ask about employees,
assets, products, orders, or related information from the database."
```

**Prompt Design Principles**:

1. **Explicit Scope Declaration**: Clear statement of purpose and limitations
2. **Rejection Instructions**: Specific directives for handling out-of-scope queries
3. **Data Context**: Description of available tables and relationships
4. **Response Guidelines**: Quality standards for answers
5. **Examples**: Demonstration of proper behavior for in/out-of-scope questions

### 4. Settings Page

**Location**: `/settings` (accessible via gear icon in navigation)

**Features**:

- **Editable System Prompt**: Large textarea for prompt customization
- **Smart Button States**:
  - Save: Disabled when no changes, blue when modified
  - Restore Default: Blue when using custom prompt, gray when already default
- **Tips Section**: Guidance on effective prompt engineering
- **Default Prompt Preview**: Shows the original scope-limited prompt

**UX Implementation**:

```typescript
// Track original prompt for change detection
const [originalPrompt, setOriginalPrompt] = useState('');

// Computed states for button logic
const hasChanged = currentPrompt.trim() !== originalPrompt.trim();
const isNotDefault = currentPrompt.trim() !== DEFAULT_PROMPT.trim();

// Button styling
<button
  disabled={!hasChanged}
  className={!hasChanged ? 'bg-gray-400' : 'bg-blue-600'}
>
  Save Changes
</button>

<button
  className={isNotDefault ? 'bg-blue-600' : 'bg-gray-400'}
>
  Restore Default
</button>
```

**Prompt Persistence**:

- Saved to localStorage immediately on "Save Changes"
- Loaded on page mount
- Sent with every chat request via `customPrompt` parameter

---

## Backend Integration

### Custom Prompt Handling

**Route**: `POST /api/ai/chat`

**Request Body**:

```typescript
{
  message: string;           // User's question
  conversationHistory: Array<{role: string, content: string}>;
  customPrompt?: string;     // Optional custom system prompt
}
```

**System Message Construction**:

```typescript
const defaultPrompt = `You are a specialized AI assistant...`; // Full default

const systemMessage = {
  role: 'system',
  content: `${customPrompt || defaultPrompt}

DATABASE CONTEXT:
${databaseContext}  // Dynamic table counts and relationships
`,
};
```

**Database Context** (Auto-injected):

```
Current database contents:
- 1,632 employees
- 1,699 assets (laptops, monitors, peripherals)
- 1,550 addresses (employee locations, warehouses, offices)
- 16 warehouses with service regions
- 5 offices
- [product/order/offboard counts]

Relationships:
- Assets can be assigned to employees (assignedTo)
- Assets can be stored in warehouses
- Employees have addresses with country, city, region
- Warehouses have addresses and serve specific countries
```

### Azure OpenAI Configuration

**Development Environment**:

```typescript
// Disable SSL verification for development
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';
```

⚠️ **Security Note**: SSL verification disabled for dev only. Re-enable for production.

**Client Configuration**:

```typescript
const client = new AzureOpenAI({
  endpoint: process.env.AZURE_OPENAI_ENDPOINT,
  apiKey: process.env.AZURE_OPENAI_KEY,
  apiVersion: '2024-02-15-preview',
});
```

**Model**: GPT-4 (configurable via environment variable)

---

## Usage Guidelines

### For End Users

**Best Practices**:

1. **Ask Specific Questions**: "How many MacBook Pros are in London?" vs "Tell me about laptops"
2. **Use Data Fields**: Reference employee names, asset serial codes, locations
3. **Request Formatting**: Ask for tables, summaries, or specific formats
4. **Iterate**: Refine questions based on initial answers

**Example Queries**:

- "Show me all assets assigned to John Smith"
- "Which warehouses serve the United Kingdom?"
- "How many employees don't have assigned laptops?"
- "List all offboarded employees from Q4 2023"
- "What's the most common laptop model in our inventory?"

**Limitations**:

- AI can only access cached Workwize data (no external information)
- Data is snapshot from last sync (not real-time)
- Complex joins may require multiple queries
- Cannot perform write operations (read-only queries)

### For Administrators

**Customizing System Prompt**:

**When to Customize**:

- Adding company-specific terminology
- Enforcing response formats (e.g., always use tables)
- Restricting to specific data subsets
- Adding compliance requirements

**Prompt Engineering Tips**:

1. **Start with Scope**: Define what the AI should/shouldn't do
2. **Be Explicit**: Use imperatives (MUST, NEVER, ALWAYS)
3. **Provide Examples**: Show desired behavior for edge cases
4. **Include Context**: Describe available data and relationships
5. **Set Standards**: Define response quality expectations

**Testing Prompt Changes**:

1. Save custom prompt in Settings
2. Clear chat history for fresh context
3. Test edge cases (in-scope, out-of-scope, ambiguous)
4. Verify response quality and scope adherence
5. Iterate based on results

---

## Configuration Reference

### Environment Variables (Backend)

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4  # Model deployment name

# Development Settings
NODE_TLS_REJECT_UNAUTHORIZED=0  # Disable SSL verification (dev only)
```

### localStorage Keys (Frontend)

| Key                | Type       | Purpose                                  |
| ------------------ | ---------- | ---------------------------------------- |
| `ai-chat-history`  | JSON Array | Persistent conversation history          |
| `ai-system-prompt` | String     | Custom system prompt (overrides default) |

**Data Formats**:

```typescript
// ai-chat-history
[
  { role: 'user', content: 'How many employees?' },
  { role: 'assistant', content: 'There are 1,632 employees...' },
];

// ai-system-prompt
('You are a specialized assistant for...'); // Plain text
```

---

## Troubleshooting

### Issue: Chat history resets on page navigation

**Cause**: localStorage not properly loaded
**Solution**: Check browser console for localStorage errors, ensure `ai-chat-history` key exists

### Issue: AI provides out-of-scope answers

**Cause**: System prompt not enforcing scope limitations
**Solution**:

1. Go to Settings page
2. Click "Restore Default" to use scope-limited prompt
3. Test with known out-of-scope questions

### Issue: Backend returns 500 error

**Causes**:

- Azure OpenAI credentials missing/invalid
- SSL certificate verification failing
- Database connection issues

**Solutions**:

- Verify environment variables in `.env`
- Check `NODE_TLS_REJECT_UNAUTHORIZED=0` for dev
- Confirm database is running and accessible

### Issue: Custom prompt not being used

**Cause**: Prompt not saved to localStorage or not sent with requests
**Solution**:

1. Open browser DevTools → Application → localStorage
2. Verify `ai-system-prompt` exists and contains custom prompt
3. Check Network tab for `/api/ai/chat` requests - should include `customPrompt` field

---

## Future Enhancements

**Planned Features**:

- [ ] Conversation export/import
- [ ] Multiple saved prompt templates
- [ ] Token usage tracking and limits
- [ ] Response regeneration
- [ ] Conversation branching
- [ ] Advanced query builder UI
- [ ] Response quality feedback
- [ ] Audit logging for queries

**Under Consideration**:

- Vector embeddings for semantic search
- Custom function calling for specific queries
- Integration with Excel export
- Scheduled report generation
- Multi-user conversation history

---

## Technical Implementation Details

### Chat Message Flow

1. **User Input**: User types question in chat interface
2. **Frontend Processing**:
   - Load custom prompt from localStorage
   - Append user message to conversation history
   - Send POST request to `/api/ai/chat` with message, history, and custom prompt
3. **Backend Processing**:
   - Construct system message (custom/default prompt + database context)
   - Build messages array: [system, ...history, user]
   - Call Azure OpenAI API
   - Stream response back to frontend
4. **Frontend Display**:
   - Render assistant response
   - Save updated conversation to localStorage
   - Update UI with new message

### Database Context Generation

**Dynamic Context Injection** (`packages/backend/src/routes/ai.ts`):

```typescript
// Query counts from database
const employeeCount = await prisma.employee.count();
const assetCount = await prisma.asset.count();
// ... other counts

// Build context string
const databaseContext = `
Current database contents:
- ${employeeCount} employees
- ${assetCount} assets
- ${addressCount} addresses
...

Relationships:
- Assets → Employees (assignedTo)
- Employees → Addresses (address)
...
`;

// Append to system message
const systemMessage = {
  role: 'system',
  content: `${customPrompt || defaultPrompt}\n\nDATABASE CONTEXT:\n${databaseContext}`,
};
```

**Benefits**:

- AI always has current data statistics
- Prevents hallucination about data availability
- Enables accurate scoping of responses
- Updates automatically as data changes

---

## Security Considerations

### Data Access

- ✅ AI has read-only access to database
- ✅ No write operations possible through AI interface
- ✅ No access to Workwize API credentials
- ✅ Cannot access files outside database

### PII Handling

- ⚠️ AI can query employee names, emails, addresses (as needed for platform functionality)
- ⚠️ Chat history stored in browser localStorage (client-side only)
- ✅ No chat history sent to external services (except Azure OpenAI for processing)
- ✅ No persistent server-side logging of conversations

### Prompt Injection

- ⚠️ Users can customize system prompt (intentional feature for administrators)
- ⚠️ No built-in prompt injection protection (trust-based model)
- ✅ Database access limited to SELECT queries only
- ✅ Prisma ORM prevents SQL injection

**Recommendations**:

1. Restrict Settings page access to administrators only (future feature)
2. Implement audit logging for prompt changes
3. Consider prompt validation to prevent malicious instructions
4. Monitor Azure OpenAI usage for abuse

---

## Performance Metrics

**Response Times** (typical):

- Simple queries (e.g., counts): 2-4 seconds
- Complex queries (e.g., multi-table joins): 4-8 seconds
- Streaming starts: ~1 second
- Database context generation: <100ms

**Resource Usage**:

- localStorage: ~10-50KB per conversation (varies with length)
- Azure OpenAI tokens: ~500-2000 per chat exchange
- Backend memory: Minimal (no conversation caching)

**Optimization Tips**:

- Clear old conversations to reduce localStorage size
- Use specific queries to reduce token usage
- Limit conversation history depth for faster responses

---

## Version History

**v2.0** (Current) - February 2026

- ✅ Persistent chat history with localStorage
- ✅ Custom system prompt support
- ✅ Settings page with smart button UX
- ✅ Clear History functionality
- ✅ Scope-limited default prompt
- ✅ Dynamic database context injection
- ✅ Azure OpenAI integration with SSL fix

**v1.0** (Initial) - January 2026

- Basic chat interface
- Fixed system prompt
- No conversation persistence
- No customization options

---

## Support and Feedback

**For Issues**:

1. Check browser console for errors
2. Verify backend is running (`http://localhost:3001/health`)
3. Confirm Azure OpenAI credentials are valid
4. Test with default prompt before reporting issues

**Feature Requests**:

- Document desired functionality
- Provide use cases and examples
- Consider security and performance implications

---

## Related Documentation

- [Initial Build Guide](INITIAL_BUILD.md) - Project setup and architecture
- [Security Guidelines](SECURITY_GUIDELINES.md) - Security best practices
- [PII Scrubbing Guidelines](PII_SCRUBBING_GUIDELINES.md) - Data handling policies
- [Database Schema](DATABASE_SCHEMA.md) - Database structure and relationships
- [Workwize APIs](WORKWIZE_APIS.md) - API reference and endpoints
