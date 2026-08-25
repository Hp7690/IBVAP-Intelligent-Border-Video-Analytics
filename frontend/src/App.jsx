import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import Admin from './pages/Admin';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import { initWebSocket } from './services/websocket';

function App() {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Initialize WebSocket connection
    const unsubscribe = initWebSocket(
      (connected) => setIsConnected(connected)
    );

    return () => unsubscribe();
  }, []);

  return (
    <Router>
      <Box sx={{ display: 'flex', height: '100vh' }}>
        <Navigation />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            overflow: 'auto',
            backgroundColor: '#121212',
          }}
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Box>
      </Box>
    </Router>
  );
}

export default App;
