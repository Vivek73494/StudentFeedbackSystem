import React from 'react';

export default function StatCard({ title, value, icon, borderColor = '#4facfe' }) {
  return (
    <div className="stat-card" style={{ borderLeftColor: borderColor }}>
      <div className="stat-info">
        <h4>{title}</h4>
        <div className="stat-value">{value}</div>
      </div>
      <div className="stat-icon">{icon}</div>
    </div>
  );
}
