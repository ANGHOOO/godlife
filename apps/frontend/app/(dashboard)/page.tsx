import { DashboardOverviewPanel } from "@/components/dashboard-overview";
import { PageHeader } from "@/components/page-header";
import { getDashboardOverviewSnapshot } from "@/lib/server/dashboard";

export default async function HomePage() {
  const overview = await getDashboardOverviewSnapshot();

  return (
    <>
      <PageHeader
        title="오늘의 운영 보드"
        subtitle="운동·독서 루틴의 현재 상태와 예외 흐름을 한 화면에서 확인합니다."
      />
      <DashboardOverviewPanel initialData={overview} />
    </>
  );
}
