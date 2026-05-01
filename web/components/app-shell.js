"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/resume-analyzer", label: "Resume Analyzer" },
  { href: "/market-dashboard", label: "Market Dashboard" },
  { href: "/skill-explorer", label: "Skill Explorer" },
  { href: "/learning-roadmap", label: "Learning Roadmap" },
];

export function AppShell({ children }) {
  const pathname = usePathname();

  return (
    <div className="site-shell">
      <header className="topbar">
        <Link href="/" className="brand">
          <span className="brand-mark">SR</span>
          <div>
            <div className="brand-name">SkillRadar</div>
            <div className="brand-tag">AI hiring intelligence for resumes and roadmaps</div>
          </div>
        </Link>
        <nav className="topnav">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={pathname === item.href ? "nav-link active" : "nav-link"}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </header>
      <main className="page-shell">{children}</main>
    </div>
  );
}
