import { PageHeader } from "@/components/page-header";
import { PlanGenerateForm } from "@/components/plan-generate-form";
import { requireCurrentSession } from "@/lib/server/auth";

export default async function PlanCreatePage() {
  await requireCurrentSession();

  return (
    <>
      <PageHeader
        title="운동 계획 생성"
        subtitle="오늘 또는 다음 날 계획을 rule/llm 소스로 생성하고 충돌을 즉시 확인합니다."
      />
      <PlanGenerateForm />
    </>
  );
}
