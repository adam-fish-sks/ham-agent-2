// Lazy-loaded Azure OpenAI to avoid startup crashes
export async function chat(messages: Array<{ role: string; content: string }>) {
  const { OpenAIClient, AzureKeyCredential } = await import('@azure/openai');

  const endpoint = process.env.AZURE_OPENAI_ENDPOINT!;
  const apiKey = process.env.AZURE_OPENAI_API_KEY!;
  const deployment = process.env.AZURE_OPENAI_DEPLOYMENT || 'gpt-4';

  // Disable SSL verification for development
  process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

  const client = new OpenAIClient(endpoint, new AzureKeyCredential(apiKey));

  try {
    const response = await client.getChatCompletions(deployment, messages);
    return response.choices[0]?.message?.content || 'No response generated';
  } catch (error) {
    console.error('Azure OpenAI error:', error);
    throw error;
  }
}
