import React from 'react';
import {
  Card,
  CardContent,
  Box,
  Typography,
  Divider,
  useTheme,
  Stack,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Info as InfoIcon,
  OpenInNew as OpenInNewIcon,
} from '@mui/icons-material';
import StatusIndicator, { StatusType } from './StatusIndicator';

export interface MetricData {
  label: string;
  value: number | string;
  type?: 'currency' | 'percentage' | 'number' | 'text';
  status?: StatusType;
  precision?: number;
  showTrend?: boolean;
  change?: number;
  changeType?: 'absolute' | 'percentage';
  subtitle?: string;
  tooltip?: string;
}

export interface MetricsCardProps {
  title: string;
  metrics: MetricData[];
  variant?: 'standard' | 'compact' | 'detailed';
  showActions?: boolean;
  onAction?: () => void;
  loading?: boolean;
  error?: string;
  lastUpdated?: Date;
  className?: string;
}

const MetricsCard: React.FC<MetricsCardProps> = ({
  title,
  metrics,
  variant = 'standard',
  showActions = false,
  onAction,
  loading = false,
  error,
  lastUpdated,
  className,
}) => {
  const theme = useTheme();

  // Get card padding based on variant
  const getCardPadding = () => {
    switch (variant) {
      case 'compact':
        return '12px';
      case 'detailed':
        return '20px';
      default:
        return '16px';
    }
  };

  // Get metric layout based on variant
  const getMetricLayout = () => {
    switch (variant) {
      case 'compact':
        return {
          direction: 'row' as const,
          spacing: 2,
          divider: <Divider orientation="vertical" flexItem />,
        };
      default:
        return {
          direction: 'column' as const,
          spacing: 1.5,
          divider: <Divider />,
        };
    }
  };

  // Render metric value
  const renderMetricValue = (metric: MetricData) => {
    const { value, type, status, precision = 2, showTrend, change, changeType } = metric;

    // For status indicators or values with trends
    if (status || showTrend || change !== undefined) {
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <StatusIndicator
            value={value}
            type={status || 'neutral'}
            variant="text"
            size={variant === 'compact' ? 'small' : 'medium'}
            format={type}
            precision={precision}
            showTrend={showTrend}
          />
          {change !== undefined && (
            <StatusIndicator
              value={change}
              type={change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'}
              variant="chip"
              size="small"
              format={changeType === 'percentage' ? 'percentage' : 'number'}
              precision={precision}
              showTrend
              prefix={changeType === 'absolute' ? (change > 0 ? '+' : '') : ''}
            />
          )}
        </Box>
      );
    }

    // Regular metric display
    return (
      <Typography
        variant={variant === 'compact' ? 'body2' : 'h6'}
        sx={{
          fontFamily: type === 'text' ? 'inherit' : theme.typography.fontFamilyMonospace,
          fontWeight: 700,
          fontSize: variant === 'compact' ? '0.875rem' : '1.125rem',
          color: theme.palette.text.primary,
        }}
      >
        {type === 'currency' && typeof value === 'number'
          ? `$${value.toLocaleString(undefined, { minimumFractionDigits: precision, maximumFractionDigits: precision })}`
          : type === 'percentage' && typeof value === 'number'
          ? `${(value * 100).toFixed(precision)}%`
          : type === 'number' && typeof value === 'number'
          ? value.toLocaleString(undefined, { minimumFractionDigits: precision, maximumFractionDigits: precision })
          : value}
      </Typography>
    );
  };

  // Render single metric
  const renderMetric = (metric: MetricData, index: number) => (
    <Box key={index} sx={{ minWidth: variant === 'compact' ? '120px' : 'auto' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
        <Typography
          variant="caption"
          sx={{
            fontSize: '0.6875rem',
            fontWeight: 600,
            letterSpacing: '0.025em',
            textTransform: 'uppercase',
            color: theme.palette.text.secondary,
          }}
        >
          {metric.label}
        </Typography>
        {metric.tooltip && (
          <Tooltip title={metric.tooltip} arrow>
            <InfoIcon
              sx={{
                fontSize: '0.75rem',
                color: theme.palette.text.disabled,
                cursor: 'help',
              }}
            />
          </Tooltip>
        )}
      </Box>
      {renderMetricValue(metric)}
      {metric.subtitle && (
        <Typography
          variant="caption"
          sx={{
            fontSize: '0.625rem',
            color: theme.palette.text.secondary,
            mt: 0.25,
            display: 'block',
          }}
        >
          {metric.subtitle}
        </Typography>
      )}
    </Box>
  );

  const layout = getMetricLayout();

  if (loading) {
    return (
      <Card className={className} sx={{ minHeight: 120 }}>
        <CardContent sx={{ padding: getCardPadding() }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 80 }}>
            <Typography variant="body2" color="text.secondary">
              Loading metrics...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className} sx={{ borderColor: theme.palette.error.light }}>
        <CardContent sx={{ padding: getCardPadding() }}>
          <Typography variant="h6" color="error" gutterBottom>
            Error Loading Metrics
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {error}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      className={className}
      sx={{
        background: 'linear-gradient(145deg, #FFFFFF 0%, #F8FAFC 100%)',
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: 1.5,
        transition: 'all 0.15s ease-in-out',
        '&:hover': {
          borderColor: theme.palette.primary.light,
          boxShadow: `0 4px 12px ${theme.palette.primary.main}15`,
        },
      }}
    >
      <CardContent sx={{ padding: getCardPadding(), '&:last-child': { paddingBottom: getCardPadding() } }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography
              variant="h6"
              sx={{
                fontSize: variant === 'compact' ? '0.875rem' : '1rem',
                fontWeight: 700,
                color: theme.palette.text.primary,
                mb: 0.5,
              }}
            >
              {title}
            </Typography>
            {lastUpdated && (
              <Typography
                variant="caption"
                sx={{
                  fontSize: '0.625rem',
                  color: theme.palette.text.disabled,
                }}
              >
                Updated {lastUpdated.toLocaleTimeString()}
              </Typography>
            )}
          </Box>
          {showActions && (
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              <Tooltip title="View details">
                <IconButton size="small" onClick={onAction}>
                  <OpenInNewIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="More options">
                <IconButton size="small">
                  <MoreVertIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          )}
        </Box>

        {/* Metrics */}
        <Stack
          direction={layout.direction}
          spacing={layout.spacing}
          divider={layout.divider}
          sx={{
            '& .MuiDivider-root': {
              borderColor: theme.palette.divider,
            },
          }}
        >
          {metrics.map((metric, index) => renderMetric(metric, index))}
        </Stack>
      </CardContent>
    </Card>
  );
};

export default MetricsCard; 