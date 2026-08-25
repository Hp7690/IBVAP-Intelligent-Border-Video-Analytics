// WebSocket service for real-time alerts
import io from 'socket.io-client';
import { useAlertStore } from '../store/alertStore';

let socket = null;
let isConnecting = false;

export const initWebSocket = (onConnectionChange) => {
  if (socket) return () => {};
  if (isConnecting) return () => {};

  isConnecting = true;

  const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const adminId = localStorage.getItem('admin_id') || 'admin_' + Date.now();

  socket = io(apiUrl, {
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: 5,
  });

  socket.on('connect', () => {
    console.log('WebSocket connected');
    onConnectionChange?.(true);
    socket.emit('admin_connect', { admin_id: adminId });
  });

  socket.on('alert', (data) => {
    console.log('Alert received:', data);
    const { addAlert } = useAlertStore.getState();
    addAlert({
      id: data.id || Date.now(),
      ...data,
      timestamp: new Date(),
    });

    // Play notification sound
    playAlertSound(data.severity);
  });

  socket.on('disconnect', () => {
    console.log('WebSocket disconnected');
    onConnectionChange?.(false);
  });

  socket.on('error', (error) => {
    console.error('WebSocket error:', error);
  });

  return () => {
    if (socket) {
      socket.disconnect();
      socket = null;
      isConnecting = false;
    }
  };
};

const playAlertSound = (severity) => {
  if (severity === 'critical') {
    // Play critical alert sound
    const audio = new Audio('data:audio/wav;base64,UklGRiYAAABXQVZFZm10IBAAAAABAAEAQB8AAAB9AAACABAAZGF0YQIAAAAAAA==');
    audio.play().catch(console.error);
  }
};

export const getSocket = () => socket;

export const sendMessage = (event, data) => {
  if (socket && socket.connected) {
    socket.emit(event, data);
  }
};
