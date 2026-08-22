import { InvestigationDetailClient } from "./InvestigationDetailClient";

export function generateStaticParams() {
  return [
    { investigationId: "INV-00000000" },
    { investigationId: "INV-001" },
  ];
}

export default function InvestigationDetailPage({
  params,
}: {
  params: { investigationId: string };
}) {
  return <InvestigationDetailClient investigationId={params.investigationId} />;
}
