"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { MetricRow } from "@/components/charts";
import { getJson, postForm, postJson } from "@/lib/api";
import { describeRole } from "@/lib/roles";

const STATUS_CLASS = {
  STRONG: "tag",
  PRESENT: "tag",
  ADJACENT: "tag warning",
  CRITICAL_GAP: "tag danger",
  RECOMMENDED_GAP: "tag warning",
};

export default function ResumeAnalyzerPage() {
  const [roles, setRoles] = useState([]);
  const [mode, setMode] = useState("manual");
  const [manualSkills, setManualSkills] = useState("");
  const [manualRole, setManualRole] = useState("");
  const [uploadRole, setUploadRole] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [weeks, setWeeks] = useState(12);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadRoles() {
      try {
        const payload = await getJson("/skills/roles", { limit: 10 });
        setRoles(payload);
        if (payload[0]?.role_key) {
          setManualRole(payload[0].role_key);
          setUploadRole(payload[0].role_key);
        }
      } catch {
        setError("Unable to load role benchmarks right now.");
      }
    }

    loadRoles();
  }, []);

  const selectedRole = mode === "manual" ? manualRole : uploadRole;
  const roleMeta = useMemo(() => roles.find((role) => role.role_key === selectedRole), [roles, selectedRole]);

  async function handleManualSubmit() {
    setLoading(true);
    setError("");
    try {
      const skills = manualSkills
        .replace(/\n/g, ",")
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
      if (!skills.length) {
        throw new Error("Add at least one skill before running manual analysis.");
      }

      const result = await postJson("/analyze/skills", {
        session_id: crypto.randomUUID(),
        target_role: manualRole,
        skills,
      });
      setAnalysis(result);
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleUploadSubmit() {
    setLoading(true);
    setError("");
    try {
      if (!resumeFile) {
        throw new Error("Upload a PDF or DOCX resume first.");
      }
      const formData = new FormData();
      formData.set("session_id", crypto.randomUUID());
      formData.set("target_role", uploadRole);
      formData.set("file", resumeFile);
      const result = await postForm("/analyze/resume", formData);
      setAnalysis(result);
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <section className="page-header">
        <h1>Resume Analyzer</h1>
        <p>
          Measure how well a profile aligns with the selected hiring benchmark using direct matches, transferable skills,
          core skill coverage, and benchmark category coverage.
        </p>
      </section>

      <div className="button-row">
        <button className={mode === "manual" ? "" : "secondary"} type="button" onClick={() => setMode("manual")}>
          Enter Skills Manually
        </button>
        <button className={mode === "upload" ? "" : "secondary"} type="button" onClick={() => setMode("upload")}>
          Upload Resume
        </button>
      </div>

      <div className="panel stack">
        <div className="control-row">
          <div className="field">
            <label htmlFor="target-role">Target role</label>
            <select
              id="target-role"
              value={selectedRole}
              onChange={(event) => (mode === "manual" ? setManualRole(event.target.value) : setUploadRole(event.target.value))}
            >
              {roles.map((role) => (
                <option key={role.role_key} value={role.role_key}>
                  {role.label}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Role context</label>
            <div className="info-strip" style={{ margin: 0 }}>
              {roleMeta ? `${roleMeta.label}: ${describeRole(roleMeta.role_key)}` : "Loading role context..."}
            </div>
          </div>
        </div>

        {mode === "manual" ? (
          <div className="field">
            <label htmlFor="manual-skills">Paste your skills</label>
            <textarea
              id="manual-skills"
              value={manualSkills}
              onChange={(event) => setManualSkills(event.target.value)}
              placeholder="Python, PyTorch, SQL, Docker, AWS"
            />
          </div>
        ) : (
          <div className="field">
            <label htmlFor="resume-file">Upload resume</label>
            <input
              id="resume-file"
              type="file"
              accept=".pdf,.docx"
              onChange={(event) => setResumeFile(event.target.files?.[0] || null)}
            />
          </div>
        )}

        <div className="button-row">
          <button type="button" onClick={mode === "manual" ? handleManualSubmit : handleUploadSubmit} disabled={loading}>
            {loading ? "Analyzing..." : "Run Analysis"}
          </button>
        </div>
      </div>

      {error ? <div className="status error">{error}</div> : null}

      {analysis ? (
        <>
          <MetricRow
            items={[
              { label: "Fit score", value: `${Math.round(analysis.gap_score)}/100` },
              { label: "Exact matches", value: analysis.summary.exact_matches },
              { label: "Adjacent matches", value: analysis.summary.adjacent_matches },
              { label: "Core skill coverage", value: `${Math.round(analysis.summary.core_skill_coverage_pct)}%` },
              { label: "Critical gaps", value: analysis.summary.critical_gaps },
            ]}
          />

          <div className="info-strip">
            Category coverage: {Math.round(analysis.summary.category_coverage_pct)}% of the tracked benchmark categories.
            Scores reward direct proof, partial credit for adjacent skills, and heavier weighting on core hiring signals.
          </div>

          <div className="split">
            <section className="panel">
              <div className="panel-header">
                <h3>What you already signal well</h3>
              </div>
              <div className="skill-list">
                {analysis.strengths.map((item) => (
                  <article key={item.skill_name} className="skill-item">
                    <div className="skill-title">
                      <span>{item.skill_name}</span>
                      <span className={STATUS_CLASS[item.status] || "tag"}>{item.status.replaceAll("_", " ")}</span>
                    </div>
                    <p className="muted">{item.reason}</p>
                    <p className="muted">Demand share: {item.market_frequency_pct.toFixed(1)}%</p>
                  </article>
                ))}
              </div>
            </section>

            <section className="panel">
              <div className="panel-header">
                <h3>What recruiters still expect</h3>
              </div>
              <div className="skill-list">
                {analysis.gaps.map((item) => (
                  <article key={item.skill_name} className="skill-item">
                    <div className="skill-title">
                      <span>{item.skill_name}</span>
                      <span className={STATUS_CLASS[item.status] || "tag warning"}>{item.status.replaceAll("_", " ")}</span>
                    </div>
                    <p className="muted">{item.reason}</p>
                    <p className="muted">Demand share: {item.market_frequency_pct.toFixed(1)}%</p>
                  </article>
                ))}
              </div>
            </section>
          </div>

          <section className="panel stack">
            <div className="panel-header">
              <h3>Build your roadmap next</h3>
              <p>Generate a role-specific learning plan from this analysis and keep the resume story moving forward.</p>
            </div>
            <div className="control-row">
              <div className="field">
                <label htmlFor="roadmap-weeks">Weeks available</label>
                <input
                  id="roadmap-weeks"
                  type="range"
                  min="4"
                  max="26"
                  value={weeks}
                  onChange={(event) => setWeeks(Number(event.target.value))}
                />
                <p className="muted">{weeks} weeks</p>
              </div>
            </div>
            <div className="button-row">
              <Link className="button-link" href={`/learning-roadmap?analysisId=${analysis.analysis_id}&weeks=${weeks}`}>
                Generate Learning Roadmap
              </Link>
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
