import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useWebSocket } from '../hooks/useWebSocket.tsx';
import { RealTimeDetection } from '../components/RealTimeDetection';
import { SecuredVideoPlayer } from '../components/SecuredVideoPlayer';
import { AlertCard } from '../components/AlertCard';
import { StatsCard } from '../components/StatsCard';
import { apiService, Camera, AnalyticsSummary } from '../services/api';
import { 
  Camera as CameraIcon, 
  AlertTriangle, 
  Users, 
  Activity,
  Eye,
  Clock,
  RefreshCw,
  Video,
  ArrowRight
} from 'lucide-react';



export const Dashboard: React.FC = () => {
  const { alerts, isConnected, getLatestAlert } = useWebSocket();
  const latestAlert = getLatestAlert();
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [analyticsSummary, setAnalyticsSummary] = useState<AnalyticsSummary>({
    total_cameras: 0,
    online_cameras: 0,
    total_detections: 0,
    total_alerts: 0,
    objects_detected_today: 0,
    system_status: 'offline',
  });

  // Fetch cameras and analytics data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch cameras
        const camerasData = await apiService.getCameras();
        // Add computed status for UI
        const camerasWithStatus = camerasData.map(camera => ({
          ...camera,
          status: (camera.is_active ? 'online' : 'offline') as 'online' | 'offline' | 'error'
        }));
        setCameras(camerasWithStatus);
        
        // Fetch analytics summary
        const summary = await apiService.getAnalyticsSummary();
        setAnalyticsSummary(summary);
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Fallback to demo data if API fails
        setCameras([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const refreshData = async () => {
    setLoading(true);
    try {
      const [camerasData, summary] = await Promise.all([
        apiService.getCameras(),
        apiService.getAnalyticsSummary()
      ]);
      const camerasWithStatus = camerasData.map(camera => ({
        ...camera,
        status: (camera.is_active ? 'online' : 'offline') as 'online' | 'offline' | 'error'
      }));
      setCameras(camerasWithStatus);
      setAnalyticsSummary(summary);
    } catch (error) {
      console.error('Error refreshing data:', error);
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    {
      title: 'Active Cameras',
      value: analyticsSummary.online_cameras,
      total: analyticsSummary.total_cameras,
      icon: CameraIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Total Alerts',
      value: alerts.length,
      icon: AlertTriangle,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
    {
      title: 'Objects Detected Today',
      value: analyticsSummary.objects_detected_today,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'System Status',
      value: analyticsSummary.system_status === 'online' ? 'Online' : 'Offline',
      icon: Activity,
      color: analyticsSummary.system_status === 'online' ? 'text-green-600' : 'text-red-600',
      bgColor: analyticsSummary.system_status === 'online' ? 'bg-green-50' : 'bg-red-50',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Monitor your security cameras and analytics</p>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={refreshData}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className="text-sm text-gray-600">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatsCard key={index} {...stat} />
        ))}
      </div>

      {/* Live video feeds */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Live Camera Feeds</h2>
          <Link
            to="/live-streams"
            className="flex items-center gap-2 px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200"
          >
            <Video className="w-4 h-4" />
            View All Streams
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
        
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading camera feeds...</p>
          </div>
        ) : cameras.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <CameraIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No cameras configured</p>
            <p className="text-sm mt-1">Add cameras to start monitoring</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {cameras.slice(0, 4).map((camera) => (
              <div key={camera.id} className="relative">
                <div className="aspect-video bg-black rounded-lg overflow-hidden">
                  <SecuredVideoPlayer
                    cameraId={camera.id.toString()}
                    muted={true}
                    playing={true}
                    onError={(error: any) => console.error(`Stream error for ${camera.id}:`, error)}
                  />
                </div>
                <div className="absolute top-2 left-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-sm">
                  {camera.name}
                </div>
                <div className="absolute top-2 right-2">
                  <div className={`w-2 h-2 rounded-full ${
                    camera.status === 'online' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent alerts */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Recent Alerts</h2>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">Last 24 hours</span>
          </div>
        </div>
        
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <AlertTriangle className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No alerts in the last 24 hours</p>
            <p className="text-sm mt-1">System is operating normally</p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.slice(0, 5).map((alert: any, index: number) => (
              <AlertCard key={index} alert={alert} />
            ))}
          </div>
        )}
      </div>

      {/* Latest alert detail */}
      {latestAlert && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Latest Alert</h2>
          <AlertCard alert={latestAlert} detailed />
        </div>
      )}

      {/* Real-time Detection Panel */}
      <RealTimeDetection />
    </div>
  );
};
