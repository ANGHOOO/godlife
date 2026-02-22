import { fetchJson } from "@/lib/client/http";
import { NotificationRetryInput, NotificationRetryResult } from "@/lib/types";

export function retryNotification(
  input: NotificationRetryInput
): Promise<NotificationRetryResult> {
  return fetchJson<NotificationRetryResult>("/api/notifications/retry", {
    method: "POST",
    body: JSON.stringify({
      notification_id: input.notificationId
    })
  });
}
