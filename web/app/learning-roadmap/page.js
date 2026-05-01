'use client';

import Link from "next/link";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { postJson } from "@/lib/api";
import { humanizeRole } from "@/lib/roles";

export default function LearningRoadmapPage() {
  const searchParams = useSearchParams();
  const analysisId = searchParams.get("analysisId") || "";
  const weeks = Number(searchParams.get("weeks") || "12");

  const [roadmap, setRoadmap] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!analysisId) {
      return;
    }

    async function loadRoadmap() {
      try {
        const result = await postJson(`/roadmap/${analysisId}?total_weeks=${weeks}`);
        setRoadmap(result);
      } catch (loadError) {
        setError(loadError.message);
      }
    }

    loadRoadmap();
  }, [analysisId, weeks]);

  return (
    <div className="stack">
      <section className="page-header">
        <h1>Learning Roadmap</h1>
        <p>Convert the benchmark gaps from your analysis into a phased plan with resources and portfolio proof ideas.</p>
      </section>

      {!analysisId ? (
        <div className="panel stack">
          <p className="muted">Generate a roadmap from Resume Analyzer first so this page has an analysis to work from.</p>
          <div className="button-row">
            <Link className="button-link" href="/resume-analyzer">
              Go To Resume Analyzer
            </Link>
          </div>
        </div>
      ) : null}

      {error ? <div className="status error">{error}</div> : null}
      {analysisId && !roadmap && !error ? <div className="status success">Generating roadmap...</div> : null}

      {roadmap ? (
        <>
          <div className="info-strip">
            <strong>{humanizeRole(roadmap.target_role)}</strong> | {roadmap.total_weeks} weeks | {roadmap.phases.length} phases
          </div>

          {roadmap.phases.length ? (
            roadmap.phases.map((phase) => (
              <section key={phase.phase_title} className="panel stack">
                <div className="panel-header">
                  <h3>
                    {phase.phase_title} | {phase.week_range}
                  </h3>
                </div>
                <div className="skill-list">
                  {phase.skills.map((skill) => (
                    <article key={`${phase.phase_title}-${skill.skill_name}`} className="skill-item">
                      <div className="skill-title">
                        <span>{skill.skill_name}</span>
                        <span className="tag">{skill.category}</span>
                      </div>
                      <p className="muted">{skill.why_important}</p>
                      <p className="muted">Estimated time: {skill.estimated_weeks} week(s)</p>
                      <p className="muted">Project proof idea: {skill.project_idea}</p>
                      <p className="muted">
                        Free resource: <a href={skill.free_resource.url} target="_blank" rel="noreferrer">{skill.free_resource.title}</a>
                      </p>
                      <p className="muted">
                        Paid resource: <a href={skill.paid_resource.url} target="_blank" rel="noreferrer">{skill.paid_resource.title}</a>
                      </p>
                    </article>
                  ))}
                </div>
              </section>
            ))
          ) : (
            <div className="status success">
              This profile already covers the tracked market benchmark unusually well. Try a different role or a leaner skill list for a sharper roadmap.
            </div>
          )}
        </>
      ) : null}
    </div>
  );
}
