import { GoogleGenerativeAI } from "@google/generative-ai";

let genAI: GoogleGenerativeAI | null = null;
let model: any = null;

const SYSTEM_PROMPT = `
You are CyberGuard AI, an expert at assisting victims of cybercrime in India.
Your goal is to help them file a formal complaint by collecting necessary details through a natural conversation.

COLLECTION GOALS:
1. Full Name
2. Type of Cybercrime (Fraud, Harassment, Identity Theft, etc.)
3. Date and Time of Incident
4. Amount Lost (if financial)
5. Suspect Details (VPA/Upi, Phone numbers, Bank accounts, etc.)
6. Detailed description of the event.

INSTRUCTIONS:
- Be empathetic and professional.
- Ask one or two questions at a time.
- If the user provides info, acknowledge it and ask the next missing field.
- When you have enough info, summarize what you've collected.
- ALWAYS respond in the USER's language.

EXTRACT FIELDS (STRICT JSON):
At the end of every response, you MUST provide a hidden JSON block if any fields are identified.
Format: [JSON_FIELDS] {"fullName": "...", "incidentType": "...", ...} [/JSON_FIELDS]
`;

export function initGemini(apiKey: string, modelName: string = "gemini-1.5-flash") {
  // Use the v1 API for stable models, especially if v1beta fails
  genAI = new GoogleGenerativeAI(apiKey);
  model = genAI.getGenerativeModel({ model: modelName }, { apiVersion: 'v1' });
}



export async function getGeminiResponse(
  chatHistory: { role: "user" | "model"; parts: { text: string }[] }[]
) {
  if (!model) {
    const apiKey = localStorage.getItem("custom_gemini_key");
    const modelName = localStorage.getItem("custom_gemini_model") || "gemini-1.5-flash";
    if (!apiKey) throw new Error("No API key available");
    initGemini(apiKey, modelName);
  }


  const chat = model.startChat({
    history: [
      {
        role: "user",
        parts: [{ text: SYSTEM_PROMPT }],
      },
      {
        role: "model",
        parts: [{ text: "Understood. I am ready to assist as CyberGuard AI." }],
      },
      ...chatHistory,
    ],
  });

  try {
    const lastMessage = chatHistory[chatHistory.length - 1].parts[0].text;
    const result = await chat.sendMessage(lastMessage);
    const response = await result.response;
    const text = response.text();

    // Extract JSON fields if present
    let collectedFields: Record<string, string> = {};
    const jsonMatch = text.match(/\[JSON_FIELDS\](.*?)\[\/JSON_FIELDS\]/s);
    if (jsonMatch) {
      try {
        collectedFields = JSON.parse(jsonMatch[1].trim());
      } catch (e) {
        console.error("Failed to parse extracted fields", e);
      }
    }

    // Clean the text of the hidden JSON block for display
    const cleanedText = text.replace(/\[JSON_FIELDS\].*?\[\/JSON_FIELDS\]/s, "").trim();

    return {
      response: cleanedText,
      collected_fields: collectedFields,
    };
  } catch (err: any) {
    console.error("Gemini SDK Error:", err);
    throw new Error(err.message || "Gemini AI failed to respond.");
  }
}

