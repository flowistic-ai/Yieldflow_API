import React, { useEffect, useState } from 'react';
import { Box, Typography, CircularProgress, CircularProgressProps } from '@mui/material';

interface AnimatedDonutProps extends CircularProgressProps {
  value: number;
}

const AnimatedDonut: React.FC<AnimatedDonutProps> = (props) => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prevProgress) => {
        if (prevProgress >= props.value) {
          clearInterval(timer);
          return props.value;
        }
        return prevProgress + 1;
      });
    }, 20);

    return () => {
      clearInterval(timer);
    };
  }, [props.value]);

  return (
    <Box sx={{ position: 'relative', display: 'inline-flex' }}>
      <CircularProgress variant="determinate" {...props} value={progress} />
      <Box
        sx={{
          top: 0,
          left: 0,
          bottom: 0,
          right: 0,
          position: 'absolute',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Typography variant="h6" component="div" color="text.primary">
          {`${Math.round(props.value)}%`}
        </Typography>
      </Box>
    </Box>
  );
};

export default AnimatedDonut; 