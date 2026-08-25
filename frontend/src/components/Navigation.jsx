import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Box,
  Tooltip,
  Badge,
  Typography,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Close as CloseIcon,
  Dashboard as DashboardIcon,
  Settings as SettingsIcon,
  BarChart as ReportsIcon,
  Admin as AdminIcon,
  Notifications as NotificationsIcon,
  LogOut as LogoutIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAlertStore } from '../store/alertStore';

function Navigation() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const { unreadCount } = useAlertStore();

  const menuItems = [
    { label: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { label: 'Admin', icon: <AdminIcon />, path: '/admin' },
    { label: 'Reports', icon: <ReportsIcon />, path: '/reports' },
    { label: 'Settings', icon: <SettingsIcon />, path: '/settings' },
  ];

  return (
    <>
      <AppBar position="fixed" sx={{ zIndex: 1300 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setOpen(!open)}
            sx={{ mr: 2 }}
          >
            {open ? <CloseIcon /> : <MenuIcon />}
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            IBVAP - Border Surveillance
          </Typography>
          <Tooltip title="Notifications">
            <IconButton color="inherit">
              <Badge badgeContent={unreadCount} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>
          <Tooltip title="Logout">
            <IconButton color="inherit">
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      <Drawer
        anchor="left"
        open={open}
        onClose={() => setOpen(false)}
        sx={{
          width: 250,
          '& .MuiDrawer-paper': {
            width: 250,
            marginTop: '64px',
            backgroundColor: '#1e1e1e',
          },
        }}
      >
        <List>
          {menuItems.map((item) => (
            <ListItem
              button
              key={item.label}
              onClick={() => {
                navigate(item.path);
                setOpen(false);
              }}
              sx={{
                '&:hover': {
                  backgroundColor: '#333',
                },
              }}
            >
              <ListItemIcon sx={{ color: '#fff' }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItem>
          ))}
        </List>
      </Drawer>

      <Box sx={{ height: '64px' }} /> {/* Offset for AppBar */}
    </>
  );
}

export default Navigation;
