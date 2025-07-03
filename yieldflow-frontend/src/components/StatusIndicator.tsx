import React from 'react';
import { Box, Chip, Typography, useTheme } from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Remove as FlatIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';

export type StatusType = 'positive' | 'negative' | 'neutral' | 'warning' | 'success' | 'error' | 'info';

export interface StatusIndicatorProps {
  value?: number | string;
  type: StatusType;
  variant?: 'chip' | 'text' | 'icon' | 'full';
  size?: 'small' | 'medium' | 'large';
  showIcon?: boolean;
  showTrend?: boolean;
  label?: string;
  format?: 'percentage' | 'currency' | 'number' | 'text';
  precision?: number;
  prefix?: string;
  suffix?: string;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  value,
  type,
  variant = 'chip',
  size = 'medium',
  showIcon = true,
  showTrend = false,
  label,
  format = 'text',
  precision = 2,
  prefix = '',
  suffix = '',
}) => {
  const theme = useTheme();

  // Format the value based on the specified format
  const formatValue = (val: number | string): string => {
    if (typeof val === 'string') return val;
    
    switch (format) {
      case 'percentage':
        return `${(val * 100).toFixed(precision)}%`;
      case 'currency':
        return `$${val.toLocaleString(undefined, { minimumFractionDigits: precision, maximumFractionDigits: precision })}`;
      case 'number':
        return val.toLocaleString(undefined, { minimumFractionDigits: precision, maximumFractionDigits: precision });
      default:
        return String(val);
    }
  };

  // Get the appropriate icon based on type and trend
  const getIcon = () => {
    if (showTrend && typeof value === 'number') {
      if (value > 0) return <TrendingUpIcon fontSize={size} />;
      if (value < 0) return <TrendingDownIcon fontSize={size} />;
      return <FlatIcon fontSize={size} />;
    }

    switch (type) {
      case 'positive':
      case 'success':
        return <CheckCircleIcon fontSize={size} />;
      case 'negative':
      case 'error':
        return <ErrorIcon fontSize={size} />;
      case 'warning':
        return <WarningIcon fontSize={size} />;
      case 'info':
        return <InfoIcon fontSize={size} />;
      default:
        return <FlatIcon fontSize={size} />;
    }
  };

  // Get colors based on type
  const getColors = () => {
    switch (type) {
      case 'positive':
        return {
          color: theme.palette.financial.positive,
          backgroundColor: theme.palette.financial.positiveBackground,
          borderColor: '#BBF7D0',
        };
      case 'negative':
        return {
          color: theme.palette.financial.negative,
          backgroundColor: theme.palette.financial.negativeBackground,
          borderColor: '#FECACA',
        };
      case 'warning':
        return {
          color: theme.palette.financial.warning,
          backgroundColor: theme.palette.financial.warningBackground,
          borderColor: '#FED7AA',
        };
      case 'neutral':
        return {
          color: theme.palette.financial.neutral,
          backgroundColor: theme.palette.financial.neutralBackground,
          borderColor: '#E5E7EB',
        };
      case 'success':
        return {
          color: theme.palette.success.main,
          backgroundColor: theme.palette.financial.positiveBackground,
          borderColor: '#BBF7D0',
        };
      case 'error':
        return {
          color: theme.palette.error.main,
          backgroundColor: theme.palette.financial.negativeBackground,
          borderColor: '#FECACA',
        };
      case 'info':
        return {
          color: theme.palette.info.main,
          backgroundColor: '#EFF6FF',
          borderColor: '#DBEAFE',
        };
      default:
        return {
          color: theme.palette.text.secondary,
          backgroundColor: theme.palette.grey[100],
          borderColor: theme.palette.grey[300],
        };
    }
  };

  const colors = getColors();
  const displayValue = value ? `${prefix}${formatValue(value)}${suffix}` : '';

  // Chip variant
  if (variant === 'chip') {
    return (
      <Chip
        icon={showIcon ? getIcon() : undefined}
        label={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {label && (
              <Typography
                variant="caption"
                sx={{
                  fontSize: '0.6875rem',
                  fontWeight: 500,
                  letterSpacing: '0.025em',
                  textTransform: 'uppercase',
                }}
              >
                {label}:
              </Typography>
            )}
            <Typography
              variant="caption"
              sx={{
                fontFamily: format === 'text' ? 'inherit' : theme.typography.fontFamilyMonospace,
                fontWeight: 600,
                fontSize: size === 'small' ? '0.625rem' : size === 'large' ? '0.875rem' : '0.75rem',
              }}
            >
              {displayValue}
            </Typography>
          </Box>
        }
        size={size === 'large' ? 'medium' : size}
        sx={{
          backgroundColor: colors.backgroundColor,
          color: colors.color,
          border: `1px solid ${colors.borderColor}`,
          fontWeight: 500,
          '& .MuiChip-icon': {
            color: colors.color,
          },
        }}
      />
    );
  }

  // Text variant
  if (variant === 'text') {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        {showIcon && (
          <Box sx={{ color: colors.color, display: 'flex', alignItems: 'center' }}>
            {getIcon()}
          </Box>
        )}
        {label && (
          <Typography
            variant="body2"
            sx={{
              color: theme.palette.text.secondary,
              fontSize: '0.75rem',
              fontWeight: 500,
            }}
          >
            {label}:
          </Typography>
        )}
        <Typography
          variant="body2"
          sx={{
            color: colors.color,
            fontFamily: format === 'text' ? 'inherit' : theme.typography.fontFamilyMonospace,
            fontWeight: 600,
            fontSize: size === 'small' ? '0.625rem' : size === 'large' ? '1rem' : '0.75rem',
          }}
        >
          {displayValue}
        </Typography>
      </Box>
    );
  }

  // Icon variant
  if (variant === 'icon') {
    return (
      <Box sx={{ color: colors.color, display: 'flex', alignItems: 'center' }}>
        {getIcon()}
      </Box>
    );
  }

  // Full variant - professional card-like display
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        padding: '6px 12px',
        borderRadius: 1,
        backgroundColor: colors.backgroundColor,
        border: `1px solid ${colors.borderColor}`,
        transition: 'all 0.15s ease-in-out',
        '&:hover': {
          boxShadow: `0 2px 8px ${colors.color}20`,
        },
      }}
    >
      {showIcon && (
        <Box sx={{ color: colors.color, display: 'flex', alignItems: 'center' }}>
          {getIcon()}
        </Box>
      )}
      <Box>
        {label && (
          <Typography
            variant="caption"
            sx={{
              display: 'block',
              color: theme.palette.text.secondary,
              fontSize: '0.6875rem',
              fontWeight: 500,
              letterSpacing: '0.025em',
              textTransform: 'uppercase',
              lineHeight: 1.2,
            }}
          >
            {label}
          </Typography>
        )}
        <Typography
          variant="body2"
          sx={{
            color: colors.color,
            fontFamily: format === 'text' ? 'inherit' : theme.typography.fontFamilyMonospace,
            fontWeight: 700,
            fontSize: size === 'small' ? '0.75rem' : size === 'large' ? '1.125rem' : '0.875rem',
            lineHeight: 1.2,
          }}
        >
          {displayValue}
        </Typography>
      </Box>
    </Box>
  );
};

export default StatusIndicator; 