import React from 'react';
import { Box, Typography } from '@mui/material';

function Dashboard() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h2" sx={{ mb: 3 }}>
        🎥 IBVAP Dashboard
      </Typography>
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Dashboard Components (to be implemented):
        </Typography>
        <ul>
          <li>Real-time Alert Panel</li>
          <li>Live Camera Grid</li>
          <li>Detection Statistics</li>
          <li>Event Timeline</li>
          <li>System Status</li>
          <li>BOP Location Map</li>
        </ul>
      </Box>
    </Box>
  );
}

export default Dashboard;
