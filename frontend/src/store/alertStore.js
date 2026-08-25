// Alert store using Zustand
import create from 'zustand';

const useAlertStore = create((set) => ({
  alerts: [],
  unreadCount: 0,
  
  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts].slice(0, 100), // Keep last 100 alerts
      unreadCount: state.unreadCount + 1,
    })),
  
  markAsRead: (alertId) =>
    set((state) => ({
      alerts: state.alerts.map((a) =>
        a.id === alertId ? { ...a, is_read: true } : a
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),
  
  clearAlerts: () =>
    set({
      alerts: [],
      unreadCount: 0,
    }),
  
  getAlertsByType: (type) =>
    set((state) => ({
      alerts: state.alerts.filter((a) => a.alert_type === type),
    })),
}));

export { useAlertStore };
