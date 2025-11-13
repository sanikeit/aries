import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface Alert {
  id: string;
  timestamp: string;
  camera_id: string;
  alert_type: string;
  confidence: number;
  object_class: string;
  object_id?: string;
  bbox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  snapshot_path?: string;
  metadata?: any;
}

export const useWebSocket = () => {
  const { token } = useAuth();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      console.log('No token available for WebSocket connection');
      return;
    }

    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;
    let heartbeatInterval: NodeJS.Timeout | null = null;

    const connect = () => {
      try {
        // Construct WebSocket URL with token as query parameter
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.hostname}:8000/ws?token=${token}`;
        
        console.log('Connecting to WebSocket:', wsUrl);
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);
          setError(null);
          
          // Start heartbeat
          heartbeatInterval = setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({ type: 'ping' }));
            }
          }, 30000); // Ping every 30 seconds
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('WebSocket message received:', data);

            if (data.type === 'pong') {
              // Heartbeat response
              return;
            }

            // Handle alert messages
            if (data.alert_type || data.camera_id) {
              const newAlert: Alert = {
                id: data.id || `alert-${Date.now()}-${Math.random()}`,
                timestamp: data.timestamp || new Date().toISOString(),
                camera_id: data.camera_id,
                alert_type: data.alert_type,
                confidence: data.confidence || 0,
                object_class: data.object_class || 'unknown',
                object_id: data.object_id,
                bbox: data.bbox || { x: 0, y: 0, width: 0, height: 0 },
                snapshot_path: data.snapshot_path,
                metadata: data.metadata,
              };

              setAlerts(prev => [newAlert, ...prev].slice(0, 100)); // Keep only last 100 alerts
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setError('WebSocket connection error');
        };

        ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          setIsConnected(false);
          
          // Clear heartbeat
          if (heartbeatInterval) {
            clearInterval(heartbeatInterval);
          }
          
          // Reconnect after 5 seconds if not a policy violation
          if (event.code !== 1008) { // 1008 = Policy Violation (invalid token)
            reconnectTimeout = setTimeout(() => {
              console.log('Attempting to reconnect...');
              connect();
            }, 5000);
          }
        };
      } catch (error) {
        console.error('Error creating WebSocket connection:', error);
        setError('Failed to create WebSocket connection');
      }
    };

    // Initial connection
    connect();

    // Cleanup function
    return () => {
      console.log('Cleaning up WebSocket connection');
      
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      
      if (heartbeatInterval) {
        clearInterval(heartbeatInterval);
      }
      
      if (ws) {
        ws.close();
      }
      
      setIsConnected(false);
      setAlerts([]);
    };
  }, [token]);

  const clearAlerts = () => {
    setAlerts([]);
  };

  const getAlertsByCamera = (cameraId: string) => {
    return alerts.filter(alert => alert.camera_id === cameraId);
  };

  const getLatestAlert = () => {
    return alerts.length > 0 ? alerts[0] : null;
  };

  return {
    alerts,
    isConnected,
    error,
    clearAlerts,
    getAlertsByCamera,
    getLatestAlert,
  };
};