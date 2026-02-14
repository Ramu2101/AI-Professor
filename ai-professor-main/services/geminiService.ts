
import { GoogleGenAI } from "@google/genai";

// Environment variable validation - Defensive Start
const API_KEY = import.meta.env.VITE_API_KEY;
if (!API_KEY) {
  // Log a critical error for the developer but ensure the app doesn't crash silently
  console.error("CRITICAL: VITE_API_KEY is missing. The Professor cannot lecture without a contract.");
}

// Initialize the 'Faculty' (AI Model)
const aiFaculty = new GoogleGenAI({ apiKey: API_KEY || "" });

/**
 * Interface representing the structured response we expect from the "Professor".
 * enforcing a schema ensures the frontend always receives predictable data.
 */
export interface LectureMaterial {
  transcript: string; // The textual explanation
  visualAidQuery: string; // A concise search query for a relevant YouTube video
}

// System instructions tailored to the "Professor" persona.
// We explicitly request JSON to ensure reliable parsing for the frontend.
const ACADEMIC_GUIDELINES = `
You are Professor Gemini, a distinguished academic known for clear, engaging, and multi-modal teaching.
Your goal is to explain complex topics simply and provide a visual reference.

INSTRUCTIONS:
1.  Explain the requested topic as if lecturing to an undergraduate class.
2.  Use a friendly but professional tone.
3.  Suggest a SPECIFIC YouTube search query that would yield a perfect visual aid for this topic (e.g., "Kurzgesagt black holes" or "MIT physics lecture gravity").
4.  YOU MUST RETURN YOUR RESPONSE IN PURE JSON FORMAT. Do not use Markdown code blocks.

JSON SCHEMA:
{
  "transcript": "Your lecture text here...",
  "visualAidQuery": "Specific YouTube Search Query"
}
`;

/**
 * Prepares a lecture for a given student query.
 * Uses a stream to deliver data progressively, mimicking a live lecture.
 *
 * @param studentQuery - The topic the student is asking about.
 * @returns A stream of the generated content.
 */
export async function prepareLecture(studentQuery: string) {
  if (!API_KEY) {
    throw new Error("Department Funding Missing: API Key is not configured.");
  }

  try {
    const lectureStream = await aiFaculty.models.generateContentStream({
      model: "gemini-2.0-flash-exp", // Using a capable model for JSON instruction following
      contents: studentQuery,
      config: {
        systemInstruction: ACADEMIC_GUIDELINES,
        responseMimeType: "application/json", // Enforce JSON response at the model level
      },
    });

    return lectureStream;
  } catch (academicException) {
    // Log the full error for debugging
    console.error("Lecture Preparation Failed:", academicException);

    // Throw a sanitized error for the UI to display
    throw new Error(" The Professor is currently on sabbatical (Connection Failed). Please try again later.");
  }
}

