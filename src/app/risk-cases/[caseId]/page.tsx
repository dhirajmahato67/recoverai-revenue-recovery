import { RiskCaseDetailClient } from "./RiskCaseDetailClient";

export function generateStaticParams() {
  return [
    { caseId: "RC-001" },
    { caseId: "RC-002" },
    { caseId: "RC-003" },
    { caseId: "RC-004" },
  ];
}

export default function RiskCaseDetailPage({
  params,
}: {
  params: { caseId: string };
}) {
  return <RiskCaseDetailClient caseId={params.caseId} />;
}
