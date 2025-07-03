import React from 'react';

interface Props {
  score: number; // 0-100
  size?: number; // diameter
}

const RiskGauge: React.FC<Props> = ({ score, size = 180 }) => {
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = Math.PI * radius; // half circle

  const clampScore = Math.max(0, Math.min(100, score));
  const percentage = clampScore / 100;
  const offset = circumference - circumference * percentage;

  // Color zones
  const getColor = () => {
    if (clampScore >= 61) return '#16a34a'; // green
    if (clampScore >= 41) return '#f59e0b'; // amber
    return '#dc2626';
  };

  const color = getColor();

  return (
    <svg width={size} height={size / 2} viewBox={`0 0 ${size} ${size / 2}`}>
      <g transform={`rotate(180 ${size / 2} ${size / 2})`}> {/* flip to start at left */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={0}
          strokeLinecap="round"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.6s ease' }}
        />
      </g>
      <text
        x="50%"
        y="95%"
        dominantBaseline="middle"
        textAnchor="middle"
        fontSize={size * 0.2}
        fontWeight="600"
        fill={color}
      >
        {clampScore}
      </text>
    </svg>
  );
};

export default RiskGauge; 