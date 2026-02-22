type StatusTone = "ok" | "fail" | "pending";

export function StatusPill({
  tone,
  label
}: {
  tone: StatusTone;
  label: string;
}) {
  const className =
    tone === "ok"
      ? "status-pill status-ok"
      : tone === "fail"
        ? "status-pill status-fail"
        : "status-pill status-pending";

  return <span className={className}>{label}</span>;
}
