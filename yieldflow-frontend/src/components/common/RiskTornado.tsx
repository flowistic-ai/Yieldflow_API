import React from 'react';
import { Box, Typography } from '@mui/material';

export interface TornadoItem {
  label: string;
  score: number; // 0-100
  color?: string;
}

interface Props {
  items: TornadoItem[];
  width?: number; // px
}

const RiskTornado: React.FC<Props> = ({ items, width = 250 }) => {
  const maxScore = Math.max(...items.map(i => i.score));
  return (
    <Box>
      {items.map(item => {
        const barWidth = (item.score / maxScore) * width;
        const color = item.color || (item.score >= 61 ? '#16a34a' : item.score >= 41 ? '#f59e0b' : '#dc2626');
        return (
          <Box key={item.label} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="body2" sx={{ width: 140 }}>{item.label}</Typography>
            <Box sx={{ flexGrow: 1, position: 'relative', height: 10, backgroundColor: '#e5e7eb', borderRadius: 5 }}>
              <Box sx={{ position: 'absolute', left: 0, top: 0, height: '100%', width: barWidth, backgroundColor: color, borderRadius: 5 }} />
            </Box>
            <Typography variant="body2" sx={{ ml: 1, width: 40, textAlign: 'right' }}>{item.score}</Typography>
          </Box>
        );
      })}
    </Box>
  );
};

export default RiskTornado; 