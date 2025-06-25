import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Container,
  Chip,
  IconButton,
  Tooltip,
  Badge,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Help as HelpIcon,
  AccountCircle as AccountCircleIcon,
  FiberManualRecord as DotIcon,
} from '@mui/icons-material';
import StatusIndicator from './StatusIndicator';

const Header: React.FC = () => {
  return (
    <AppBar 
      position="sticky" 
      elevation={0}
      sx={{ 
        background: 'linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
        backdropFilter: 'blur(10px)',
        height: 72,
      }}
    >
      <Container maxWidth="xl">
        <Toolbar sx={{ 
          py: 1, 
          justifyContent: 'space-between',
          minHeight: '72px !important',
          alignItems: 'center'
        }}>
          {/* Logo and Title */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2.5 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 44,
                height: 44,
                borderRadius: 1.5,
                background: 'linear-gradient(135deg, #059669 0%, #10B981 100%)',
                boxShadow: '0 3px 10px rgba(5, 150, 105, 0.4)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
              }}
            >
              <TrendingUpIcon sx={{ color: 'white', fontSize: 24 }} />
            </Box>
            <Box>
              <Typography 
                variant="h5" 
                component="div" 
                sx={{ 
                  color: 'white',
                  fontWeight: 700,
                  fontSize: '1.375rem',
                  letterSpacing: '-0.025em',
                  lineHeight: 1.2,
                }}
              >
                YieldFlow
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.65)',
                  fontSize: '0.6875rem',
                  fontWeight: 500,
                  letterSpacing: '0.025em',
                  textTransform: 'uppercase',
                  mt: -0.25,
                  display: 'block',
                }}
              >
                Professional Financial Analysis
              </Typography>
            </Box>
          </Box>

          {/* Center Status Section */}
          <Box sx={{ 
            display: { xs: 'none', md: 'flex' }, 
            alignItems: 'center', 
            gap: 2,
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: 1,
            padding: '6px 12px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <DotIcon sx={{ color: '#10B981', fontSize: 12 }} />
              <Typography variant="caption" sx={{ 
                color: 'rgba(255, 255, 255, 0.8)',
                fontSize: '0.6875rem',
                fontWeight: 500,
              }}>
                Live Market Data
              </Typography>
            </Box>
            <Box sx={{ width: 1, height: 16, backgroundColor: 'rgba(255, 255, 255, 0.2)' }} />
            <Typography variant="caption" sx={{ 
              color: 'rgba(255, 255, 255, 0.6)',
              fontSize: '0.6875rem',
              fontFamily: 'JetBrains Mono, monospace',
            }}>
              {new Date().toLocaleTimeString()}
            </Typography>
          </Box>

          {/* Actions and Status */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            {/* Status Chips */}
            <Box sx={{ 
              display: { xs: 'none', lg: 'flex' }, 
              alignItems: 'center', 
              gap: 1.5 
            }}>
              <Chip
                icon={<SecurityIcon sx={{ fontSize: '0.875rem !important' }} />}
                label="Enterprise"
                size="small"
                sx={{
                  backgroundColor: 'rgba(5, 150, 105, 0.15)',
                  color: '#10B981',
                  border: '1px solid rgba(16, 185, 129, 0.25)',
                  fontWeight: 600,
                  fontSize: '0.6875rem',
                  height: 24,
                  '& .MuiChip-icon': {
                    color: '#10B981',
                  },
                  '& .MuiChip-label': {
                    padding: '0 6px',
                  },
                }}
              />
              <StatusIndicator
                type="positive"
                variant="chip"
                size="small"
                value="Connected"
                showIcon={false}
              />
            </Box>

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Tooltip title="Notifications" arrow>
                <IconButton 
                  size="small" 
                  sx={{ 
                    color: 'rgba(255, 255, 255, 0.7)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      color: 'white',
                    },
                  }}
                >
                  <Badge badgeContent={3} color="error">
                    <NotificationsIcon fontSize="small" />
                  </Badge>
                </IconButton>
              </Tooltip>

              <Tooltip title="Help & Documentation" arrow>
                <IconButton 
                  size="small" 
                  sx={{ 
                    color: 'rgba(255, 255, 255, 0.7)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      color: 'white',
                    },
                  }}
                >
                  <HelpIcon fontSize="small" />
                </IconButton>
              </Tooltip>

              <Tooltip title="Settings" arrow>
                <IconButton 
                  size="small" 
                  sx={{ 
                    color: 'rgba(255, 255, 255, 0.7)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      color: 'white',
                    },
                  }}
                >
                  <SettingsIcon fontSize="small" />
                </IconButton>
              </Tooltip>

              <Box sx={{ width: 1, height: 20, backgroundColor: 'rgba(255, 255, 255, 0.2)', mx: 1 }} />

              <Tooltip title="Account" arrow>
                <IconButton 
                  size="small" 
                  sx={{ 
                    color: 'rgba(255, 255, 255, 0.7)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      color: 'white',
                    },
                  }}
                >
                  <AccountCircleIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header; 