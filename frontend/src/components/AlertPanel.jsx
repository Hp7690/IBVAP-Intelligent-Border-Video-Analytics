import React from 'react';
import { Card, CardContent, CardHeader, Box, Typography } from '@mui/material';

function AlertPanel({ alerts }) {
  return (
    <Card sx={{ mb: 2 }}>
      <CardHeader title="Real-time Alerts" />
      <CardContent>
        {alerts.length === 0 ? (
          <Typography color="textSecondary">No alerts</Typography>
        ) : (
          <Box sx={{ maxHeight: '500px', overflowY: 'auto' }}>
            {alerts.map((alert) => (
              <Box
                key={alert.id}
                className={`alert-${alert.severity} fade-in`}
                sx={{
                  p: 2,
                  mb: 1,
                  borderRadius: 1,
                  color: '#fff',
                }}
              >
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                  {alert.alert_type}
                </Typography>
                <Typography variant="body2">{alert.message}</Typography>
                <Typography variant="caption" sx={{ opacity: 0.7 }}>
                  {new Date(alert.timestamp).toLocaleString()}
                </Typography>
              </Box>
            ))}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

export default AlertPanel;
