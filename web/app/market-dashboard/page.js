"use client";

import { useEffect, useMemo, useState } from "react";

import { HeatmapGrid, HorizontalBarCard, MetricRow, TrendLineCard } from "@/components/charts";
import { getJson } from "@/lib/api";
import { describeRole, humanizeRole } from "@/lib/roles";

const CATEGORY_COLORS = {
  language: "#2563eb",
  framework: "#0f766e",
  tool: "#f59e0b",
  concept: "#7c3aed",
  cloud: "#dc2626",
  domain: "#0891b2",
  other: "#64748b",
};

export default function MarketDashboardPage() {
  const [roles, setRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState("all");
  const [summary, setSummary] = useState(null);
  const [topSkills, setTopSkills] = useState([]);
  const [trending, setTrending] = useState({ rising: [], falling: [] });
  const [heatmap, setHeatmap] = useState({ skills: [], weeks: [], matrix: [] });
  const [statusMessage, setStatusMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadRoles() {
      try {
        const [roleItems, scrapeStatus] = await Promise.all([
          getJson("/skills/roles", { limit: 10 }),
          getJson("/scrape/status"),
        ]);
        setRoles(roleItems);
        const scrapedTotal = Object.values(scrapeStatus.posting_counts || {}).reduce((sum, value) => sum + value, 0);
        setStatusMessage(
          scrapedTotal > 0
            ? `This demo is backed by ${scrapedTotal} scraped postings plus the tracked market aggregates.`
            : "This demo is backed by a curated 12-week hiring snapshot across 10 AI and data roles."
        );
      } catch (loadError) {
        setError(loadError.message);
      }
    }

    loadRoles();
  }, []);

  useEffect(() => {
    async function loadDashboard() {
      setLoading(true);
      setError("");
      try {
        const [summaryPayload, topSkillsPayload, trendingPayload, heatmapPayload] = await Promise.all([
          getJson("/skills/summary", { role_filter: selectedRole }),
          getJson("/skills/top", { role_filter: selectedRole, limit: 12 }),
          getJson("/skills/trending", { role_filter: selectedRole }),
          getJson("/skills/heatmap", { role_filter: selectedRole }),
        ]);
        setSummary(summaryPayload);
        setTopSkills(topSkillsPayload);
        setTrending(trendingPayload);
        setHeatmap(heatmapPayload);
      } catch (loadError) {
        setError(loadError.message);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, [selectedRole]);

  const selectedRoleMeta = useMemo(
    () => roles.find((role) => role.role_key === selectedRole),
    [roles, selectedRole],
  );

  const velocityRows = useMemo(
    () =>
      [
        ...trending.rising.slice(0, 8).map((item) => ({ ...item, direction: "Rising" })),
        ...trending.falling.slice(0, 4).map((item) => ({ ...item, direction: "Cooling" })),
      ],
    [trending],
  );

  const topSkillTrendRows = useMemo(() => {
    const focusSkills = new Set(topSkills.slice(0, 5).map((item) => item.skill_name));
    return heatmap.weeks.map((week, columnIndex) => {
      const row = { week_start: week.slice(5) };
      heatmap.skills.forEach((skill, rowIndex) => {
        if (focusSkills.has(skill)) {
          row[skill] = heatmap.matrix[rowIndex]?.[columnIndex] || 0;
        }
      });
      return row;
    });
  }, [heatmap, topSkills]);

  const trendSeries = topSkills.slice(0, 5).map((item, index) => ({
    key: item.skill_name,
    label: item.skill_name,
    color: ["#0f766e", "#2563eb", "#f59e0b", "#7c3aed", "#dc2626"][index % 5],
  }));

  return (
    <div className="stack">
      <section className="page-header">
        <h1>Market Dashboard</h1>
        <p>Track which skills dominate a role, which ones are accelerating, and how the benchmark has moved week by week.</p>
      </section>

      <div className="control-row">
        <div className="field">
          <label htmlFor="role-view">Role view</label>
          <select id="role-view" value={selectedRole} onChange={(event) => setSelectedRole(event.target.value)}>
            <option value="all">All Roles</option>
            {roles.map((role) => (
              <option key={role.role_key} value={role.role_key}>
                {role.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {statusMessage ? <div className="info-strip">{statusMessage}</div> : null}

      {selectedRoleMeta ? (
        <div className="info-strip">
          <strong>{selectedRoleMeta.label}</strong> | {describeRole(selectedRole)} | Latest tracked postings:{" "}
          {selectedRoleMeta.latest_postings} | Week-over-week change: {selectedRoleMeta.week_over_week_change_pct > 0 ? "+" : ""}
          {selectedRoleMeta.week_over_week_change_pct}% | Top requested skill: {selectedRoleMeta.top_skill || "N/A"}
        </div>
      ) : (
        <div className="info-strip">
          <strong>{humanizeRole(selectedRole)}</strong> | {describeRole(selectedRole)}
        </div>
      )}

      {error ? <div className="status error">{error}</div> : null}
      {loading || !summary ? <div className="status success">Loading dashboard...</div> : null}

      {summary ? (
        <>
          <MetricRow
            items={[
              { label: "Tracked postings", value: summary.total_postings },
              { label: "Unique tracked skills", value: summary.unique_skills },
              { label: "Top skill", value: summary.top_skill || "N/A" },
              { label: "Fastest rising", value: summary.fastest_rising || "N/A" },
              { label: "Latest snapshot week", value: summary.data_freshness_week || "N/A" },
            ]}
          />

          <div className="two-column">
            <HorizontalBarCard
              title={`Top skills for ${humanizeRole(selectedRole)}`}
              data={[...topSkills].sort((left, right) => left.frequency_pct - right.frequency_pct)}
              dataKey="frequency_pct"
              colorKey="category"
              colors={CATEGORY_COLORS}
            />
            <HorizontalBarCard
              title="Momentum this quarter"
              data={[...velocityRows].sort((left, right) => left.velocity - right.velocity)}
              dataKey="velocity"
              colorKey="direction"
              colors={{ Rising: "#15803d", Cooling: "#dc2626" }}
            />
          </div>

          {topSkillTrendRows.length > 0 ? (
            <TrendLineCard title="How the top skills moved over 12 weeks" data={topSkillTrendRows} series={trendSeries} />
          ) : null}

          <HeatmapGrid title="Tracked skill demand by week" payload={heatmap} />
        </>
      ) : null}
    </div>
  );
}
