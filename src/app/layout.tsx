import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { AppShell } from "@/components/layout/AppShell";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

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
    <html lang="en" suppressHydrationWarning className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen font-sans bg-background antialiased selection:bg-neutral-200 dark:selection:bg-neutral-800">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
