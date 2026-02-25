import { AzureOpenAI } from '@azure/openai';

const endpoint = process.env.AZURE_OPENAI_ENDPOINT!;
const apiKey = process.env.AZURE_OPENAI_API_KEY!;
const deployment = process.env.AZURE_OPENAI_DEPLOYMENT!;

export const openai = new AzureOpenAI({
  endpoint,
  apiKey,
  deployment,
  apiVersion: '2024-02-15-preview',
});

export async function chat(messages: Array<{ role: string; content: string }>) {
  try {
    const response = await openai.chat.completions.create({
      model: deployment,
      messages: messages as any,
      temperature: 0.7,
      max_tokens: 1000,
    });

    return response.choices[0]?.message?.content || 'No response generated';
  } catch (error) {
    console.error('Azure OpenAI error:', error);
    throw error;
  }
}
