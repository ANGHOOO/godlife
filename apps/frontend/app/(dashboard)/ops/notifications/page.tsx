import { NotificationRetryForm } from "@/components/notification-retry-form";
import { PageHeader } from "@/components/page-header";

export default function NotificationsOpsPage() {
  return (
    <>
      <PageHeader
        title="알림 재시도 운영"
        subtitle="전송 실패 또는 지연된 알림을 수동으로 재시도하고 상태를 확인합니다."
      />
      <NotificationRetryForm />
    </>
  );
}
