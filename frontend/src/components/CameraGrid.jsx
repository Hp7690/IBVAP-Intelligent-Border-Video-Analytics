import React from 'react';
import { Card, CardContent, CardHeader, Box, Typography, Grid } from '@mui/material';

function CameraGrid({ cameras }) {
  return (
    <Card>
      <CardHeader title="Live Camera Feeds" />
      <CardContent>
        <Grid container spacing={2}>
          {cameras.length === 0 ? (
            <Grid item xs={12}>
              <Typography color="textSecondary">No cameras connected</Typography>
            </Grid>
          ) : (
            cameras.map((camera) => (
              <Grid item xs={12} sm={6} md={4} key={camera.id}>
                <Box
                  sx={{
                    aspectRatio: '16/9',
                    backgroundColor: '#000',
                    borderRadius: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    border: '1px solid #333',
                  }}
                >
                  <Typography variant="body2" color="textSecondary">
                    {camera.name} - {camera.bop_id}
                  </Typography>
                </Box>
              </Grid>
            ))
          )}
        </Grid>
      </CardContent>
    </Card>
  );
}

export default CameraGrid;
