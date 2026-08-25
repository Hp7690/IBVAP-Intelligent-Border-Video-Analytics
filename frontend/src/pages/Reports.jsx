import React from 'react';
import { Box, Typography } from '@mui/material';

function Reports() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h2" sx={{ mb: 3 }}>
        📊 Reports
      </Typography>
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Report Features (to be implemented):
        </Typography>
        <ul>
          <li>Detection Analytics</li>
          <li>Alert History</li>
          <li>Incident Reports</li>
          <li>Camera Performance</li>
          <li>Activity Trends</li>
          <li>Export Reports</li>
        </ul>
      </Box>
    </Box>
  );
}

export default Reports;
