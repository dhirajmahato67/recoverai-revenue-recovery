import { RecoveryExecutionClient } from "./RecoveryExecutionClient";

export function generateStaticParams() {
  return [
    { batchId: "RB-022" },
    { batchId: "RB-023" },
    { batchId: "RB-024" },
    { batchId: "RB-025" },
  ];
}

export default function RecoveryExecutionPage({
  params,
}: {
  params: { batchId: string };
}) {
  return <RecoveryExecutionClient batchId={params.batchId} />;
}
