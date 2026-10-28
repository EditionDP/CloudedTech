import { apiRequest } from "./client";

export interface NotificationPreferences {
  highlights_enabled: boolean;
  sentiment_enabled: boolean;
  approvals_enabled: boolean;
}

const ENDPOINT = "/api/v1/notification-preferences";

export async function getNotificationPreferences(): Promise<NotificationPreferences> {
  return (await apiRequest(ENDPOINT, {
    method: "GET",
  })) as NotificationPreferences;
}

export async function saveNotificationPreferences(
  preferences: NotificationPreferences
): Promise<NotificationPreferences> {
  return (await apiRequest(ENDPOINT, {
    method: "PUT",
    body: JSON.stringify(preferences),
  })) as NotificationPreferences;
}