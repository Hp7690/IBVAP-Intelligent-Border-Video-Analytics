import React from 'react';
import { Box, Typography } from '@mui/material';

function Admin() {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h2" sx={{ mb: 3 }}>
        ⚙️ Admin Panel
      </Typography>
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" sx={{ mb: 2 }}>
          Admin Features (to be implemented):
        </Typography>
        <ul>
          <li>System Configuration</li>
          <li>Camera Management</li>
          <li>User Management</li>
          <li>Alert Rules Configuration</li>
          <li>Zone Management</li>
          <li>System Health Monitoring</li>
        </ul>
      </Box>
    </Box>
  );
}

export default Admin;
