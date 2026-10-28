import { apiRequest } from "./client";

export interface MotorAiSettings {
  provider: string;
  model: string;
  temperature: number;
  mode: string;
  provider_verified: boolean;
  provider_status: string;
  description: string;
}

export async function getMotorAiSettings(): Promise<MotorAiSettings> {
  const data = await apiRequest(
    "/api/v1/content-workflow/ai-settings"
  ) as MotorAiSettings;

  if (
    !data ||
    typeof data.provider !== "string" ||
    typeof data.model !== "string" ||
    typeof data.temperature !== "number" ||
    typeof data.provider_verified !== "boolean"
  ) {
    throw new Error(
      "El Motor IA devolvio una configuracion no valida."
    );
  }

  return data;
}