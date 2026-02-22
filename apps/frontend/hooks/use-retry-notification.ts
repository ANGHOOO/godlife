"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { retryNotification } from "@/lib/client/notifications";
import { NotificationRetryInput } from "@/lib/types";

export function useRetryNotification() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: NotificationRetryInput) => retryNotification(input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["dashboard-overview"] });
    }
  });
}
