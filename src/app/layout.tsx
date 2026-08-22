import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/layout/AppShell";

export const metadata: Metadata = {
  title: "RecoverAI — Production-Grade AI Revenue Recovery Platform",
  description: "Find lost revenue. Recover it safely. Prove the impact. AI-powered revenue recovery control center for merchants.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full overflow-hidden" suppressHydrationWarning>
      <body className="h-full overflow-hidden font-sans bg-background antialiased selection:bg-neutral-200 dark:selection:bg-neutral-800">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
