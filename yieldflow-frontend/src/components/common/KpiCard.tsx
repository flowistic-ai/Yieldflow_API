import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

interface KpiCardProps {
  label: string;
  value: string | number;
  unit?: string;
  prefix?: string;
}

const KpiCard: React.FC<KpiCardProps> = ({ label, value, unit, prefix }) => {
  const displayValue = typeof value === 'number' ? value.toFixed(2) : value;

  return (
    <Paper
      variant="outlined"
      sx={{
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: 2,
        minWidth: 120,
        textAlign: 'center',
        borderColor: 'rgba(0, 0, 0, 0.12)',
        '&:hover': {
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          transform: 'translateY(-2px)',
        },
        transition: 'all 0.2s ease-in-out',
      }}
    >
      <Typography variant="h6" fontWeight="bold">
        {prefix}{displayValue}{unit}
      </Typography>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
    </Paper>
  );
};

export default KpiCard; 