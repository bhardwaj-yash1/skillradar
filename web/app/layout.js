import "./globals.css";
export const dynamic = 'force-dynamic';
import { AppShell } from "@/components/app-shell";

export const metadata = {
  title: "SkillRadar",
  description: "AI hiring intelligence for resumes, skill benchmarks, and learning roadmaps.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
