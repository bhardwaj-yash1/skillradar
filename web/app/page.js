import Link from "next/link";

export default function HomePage() {
  return (
    <div className="stack">
      <section className="hero">
        <span className="eyebrow">Live AI Career Demo</span>
        <h1>See how your resume stacks up against today&apos;s AI hiring market.</h1>
        <p>
          SkillRadar benchmarks resumes against tracked AI and data roles, surfaces the skills recruiters
          are actually asking for, and turns missing signals into a practical learning roadmap.
        </p>
        <div className="button-row" style={{ marginTop: "1.25rem" }}>
          <Link className="button-link" href="/resume-analyzer">
            Start With Resume Analyzer
          </Link>
          <Link className="button-link secondary" href="/market-dashboard">
            Explore Market Dashboard
          </Link>
        </div>
        <div className="hero-grid">
          <section className="panel">
            <div className="panel-header">
              <h3>What recruiters can test here</h3>
            </div>
            <div className="stack muted">
              <p>Compare role demand across AI Engineer, ML Engineer, LLM Engineer, Data Scientist, and more.</p>
              <p>Inspect which skills are rising, stable, or cooling over a 12-week market snapshot.</p>
              <p>Upload a resume or paste skills and get a role-specific fit score plus a roadmap.</p>
            </div>
          </section>
          <section className="panel">
            <div className="panel-header">
              <h3>Best demo flow</h3>
            </div>
            <div className="stack muted">
              <p>1. Start with Resume Analyzer.</p>
              <p>2. Open Market Dashboard to understand the benchmark behind the score.</p>
              <p>3. Use Skill Explorer to inspect one requirement in detail.</p>
              <p>4. Finish with the generated learning roadmap.</p>
            </div>
          </section>
        </div>
      </section>
    </div>
  );
}
