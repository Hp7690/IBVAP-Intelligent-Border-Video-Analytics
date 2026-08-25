import React from 'react';
import { Box, Typography } from '@mui/material';

function Settings() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h2" sx={{ mb: 3 }}>
        ⚙️ Settings
      </Typography>
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Settings Options (to be implemented):
        </Typography>
        <ul>
          <li>Detection Thresholds</li>
          <li>Alert Preferences</li>
          <li>Night Mode Settings</li>
          <li>User Preferences</li>
          <li>API Configuration</li>
          <li>Data Retention Policies</li>
        </ul>
      </Box>
    </Box>
  );
}

export default Settings;
