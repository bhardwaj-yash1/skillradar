"use client";

import { useEffect, useMemo, useState } from "react";

import { HorizontalBarCard, MetricRow, TrendLineCard } from "@/components/charts";
import { getJson } from "@/lib/api";
import { describeRole, humanizeRole } from "@/lib/roles";

export default function SkillExplorerPage() {
  const [roles, setRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState("ml_engineer");
  const [skills, setSkills] = useState([]);
  const [selectedSkill, setSelectedSkill] = useState("");
  const [roleTrend, setRoleTrend] = useState([]);
  const [overallTrend, setOverallTrend] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadRoles() {
      try {
        const roleItems = await getJson("/skills/roles", { limit: 10 });
        setRoles(roleItems);
        if (roleItems[0]?.role_key) {
          setSelectedRole(roleItems[0].role_key);
        }
      } catch (loadError) {
        setError(loadError.message);
      }
    }

    loadRoles();
  }, []);

  useEffect(() => {
    if (!selectedRole) {
      return;
    }

    async function loadSkills() {
      try {
        const topSkills = await getJson("/skills/top", { role_filter: selectedRole, limit: 25 });
        setSkills(topSkills);
        setSelectedSkill((current) => current || topSkills[0]?.skill_name || "");
      } catch (loadError) {
        setError(loadError.message);
      }
    }

    loadSkills();
  }, [selectedRole]);

  useEffect(() => {
    if (!selectedRole || !selectedSkill) {
      return;
    }

    async function loadTrend() {
      try {
        const [rolePayload, overallPayload] = await Promise.all([
          getJson(`/skills/trend/${encodeURIComponent(selectedSkill)}`, {
            role_filter: selectedRole,
            weeks: 12,
          }),
          getJson(`/skills/trend/${encodeURIComponent(selectedSkill)}`, {
            role_filter: "all",
            weeks: 12,
          }),
        ]);
        setRoleTrend(rolePayload.points || []);
        setOverallTrend(overallPayload.points || []);
      } catch (loadError) {
        setError(loadError.message);
      }
    }

    loadTrend();
  }, [selectedRole, selectedSkill]);

  const selectedRoleMeta = useMemo(
    () => roles.find((role) => role.role_key === selectedRole),
    [roles, selectedRole],
  );
  const selectedSkillMeta = useMemo(
    () => skills.find((skill) => skill.skill_name === selectedSkill),
    [skills, selectedSkill],
  );
  const roleRank = useMemo(
    () => Math.max(0, skills.findIndex((skill) => skill.skill_name === selectedSkill)) + 1,
    [skills, selectedSkill],
  );

  const trendRows = useMemo(
    () =>
      roleTrend.map((point, index) => ({
        week_start: point.week_start.slice(5),
        roleBenchmark: point.frequency_pct,
        overallMarket: overallTrend[index]?.frequency_pct || 0,
      })),
    [roleTrend, overallTrend],
  );

  const benchmarkRows = [...skills]
    .slice(0, 10)
    .map((skill) => ({ ...skill, highlight: skill.skill_name === selectedSkill ? "Selected skill" : "Other top skill" }))
    .sort((left, right) => left.frequency_pct - right.frequency_pct);

  const currentRoleDemand = roleTrend.at(-1)?.frequency_pct || 0;
  const currentOverallDemand = overallTrend.at(-1)?.frequency_pct || 0;
  const velocity = roleTrend.length >= 2 ? currentRoleDemand - roleTrend[0].frequency_pct : 0;
  const peak = roleTrend.reduce(
    (best, point) => (point.frequency_pct > best.frequency_pct ? point : best),
    roleTrend[0] || { frequency_pct: 0, week_start: "N/A" },
  );

  return (
    <div className="stack">
      <section className="page-header">
        <h1>Skill Explorer</h1>
        <p>Compare one skill&apos;s role-specific demand against the broader market and show where it sits in the hiring benchmark.</p>
      </section>

      <div className="control-row">
        <div className="field">
          <label htmlFor="role-benchmark">Role benchmark</label>
          <select id="role-benchmark" value={selectedRole} onChange={(event) => setSelectedRole(event.target.value)}>
            {roles.map((role) => (
              <option key={role.role_key} value={role.role_key}>
                {role.label}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="skill-select">Skill to inspect</label>
          <select id="skill-select" value={selectedSkill} onChange={(event) => setSelectedSkill(event.target.value)}>
            {skills.map((skill) => (
              <option key={skill.skill_name} value={skill.skill_name}>
                {skill.skill_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {selectedRoleMeta ? (
        <div className="info-strip">
          <strong>{selectedRoleMeta.label}</strong> | {describeRole(selectedRole)} | Tracked postings: {selectedRoleMeta.latest_postings} |
          Top requested skill: {selectedRoleMeta.top_skill || "N/A"}
        </div>
      ) : null}

      {error ? <div className="status error">{error}</div> : null}

      {selectedSkill ? (
        <>
          <MetricRow
            items={[
              { label: "Current role demand", value: `${currentRoleDemand.toFixed(1)}%` },
              { label: "Overall market demand", value: `${currentOverallDemand.toFixed(1)}%` },
              { label: "12-week change", value: `${velocity > 0 ? "+" : ""}${velocity.toFixed(1)} pts` },
              { label: "Peak week", value: peak.week_start.slice ? peak.week_start.slice(5) : peak.week_start },
              { label: "Role rank", value: roleRank ? `#${roleRank}` : "N/A" },
            ]}
          />

          <TrendLineCard
            title={`${selectedSkill} demand trend`}
            data={trendRows}
            series={[
              { key: "roleBenchmark", label: humanizeRole(selectedRole), color: "#0f766e" },
              { key: "overallMarket", label: "Overall market", color: "#64748b", dashed: true, strokeWidth: 2 },
            ]}
          />

          <HorizontalBarCard
            title={`Where ${selectedSkill} sits inside ${humanizeRole(selectedRole)}`}
            data={benchmarkRows}
            dataKey="frequency_pct"
            colorKey="highlight"
            colors={{ "Selected skill": "#0f766e", "Other top skill": "#cbd5e1" }}
          />

          {selectedSkillMeta ? (
            <div className="info-strip">
              <strong>{selectedSkillMeta.skill_name}</strong> currently falls under the <strong>{selectedSkillMeta.category}</strong> category
              and sits inside the top {roleRank} tracked skills for {humanizeRole(selectedRole)}.
            </div>
          ) : null}
        </>
      ) : null}
    </div>
  );
}
