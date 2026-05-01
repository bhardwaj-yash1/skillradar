"use client";

import { Fragment } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export function MetricRow({ items }) {
  return (
    <div className="metric-grid">
      {items.map((item) => (
        <article key={item.label} className="metric-card">
          <p className="metric-label">{item.label}</p>
          <h3 className="metric-value">{item.value}</h3>
          {item.helper ? <p className="metric-helper">{item.helper}</p> : null}
        </article>
      ))}
    </div>
  );
}

export function HorizontalBarCard({ title, data, dataKey, colorKey = "category", colors = {} }) {
  return (
    <section className="panel chart-panel">
      <div className="panel-header">
        <h3>{title}</h3>
      </div>
      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height={360}>
          <BarChart data={data} layout="vertical" margin={{ left: 16, right: 16, top: 8, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#d9e3e8" />
            <XAxis type="number" />
            <YAxis type="category" dataKey="skill_name" width={120} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey={dataKey} radius={[0, 8, 8, 0]}>
              {data.map((entry) => (
                <Cell key={`${entry.skill_name}-${entry[colorKey]}`} fill={colors[entry[colorKey]] || "#0f766e"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export function TrendLineCard({ title, data, series }) {
  return (
    <section className="panel chart-panel">
      <div className="panel-header">
        <h3>{title}</h3>
      </div>
      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height={360}>
          <LineChart data={data} margin={{ left: 8, right: 16, top: 8, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#d9e3e8" />
            <XAxis dataKey="week_start" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            {series.map((item) => (
              <Line
                key={item.key}
                type="monotone"
                dataKey={item.key}
                stroke={item.color}
                strokeWidth={item.strokeWidth || 3}
                dot={{ r: 3 }}
                strokeDasharray={item.dashed ? "6 4" : undefined}
                name={item.label}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}

export function HeatmapGrid({ title, payload }) {
  const { skills = [], weeks = [], matrix = [] } = payload || {};

  return (
    <section className="panel">
      <div className="panel-header">
        <h3>{title}</h3>
        <p>Darker cells indicate that the skill appeared in a larger share of tracked postings that week.</p>
      </div>
      <div className="heatmap-grid">
        <div className="heatmap-corner" />
        {weeks.map((week) => (
          <div key={week} className="heatmap-week">
            {week.slice(5)}
          </div>
        ))}
        {skills.map((skill, rowIndex) => (
          <Fragment key={skill}>
            <div className="heatmap-skill">{skill}</div>
            {weeks.map((week, columnIndex) => {
              const value = matrix[rowIndex]?.[columnIndex] || 0;
              const opacity = Math.max(0.12, Math.min(1, value / 80));
              return (
                <div
                  key={`${skill}-${week}`}
                  className="heatmap-cell"
                  style={{ backgroundColor: `rgba(15, 118, 110, ${opacity})` }}
                  title={`${skill} | ${week} | ${value.toFixed(1)}%`}
                >
                  {value.toFixed(0)}
                </div>
              );
            })}
          </Fragment>
        ))}
      </div>
    </section>
  );
}
