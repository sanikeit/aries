import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { 
  BarChart, 
  TrendingUp, 
  Users, 
  Car, 
  Clock,
  RefreshCw,
  Filter,
  Download
} from 'lucide-react';

interface DetectionStats {
  total_detections: number;
  detections_by_class: Record<string, number>;
  hourly_detections: Array<{
    hour: string;
    count: number;
  }>;
  top_objects: Array<{
    class_name: string;
    count: number;
  }>;
  time_range: string;
}

export const Analytics: React.FC = () => {
  const [stats, setStats] = useState<DetectionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('24h');
  const [selectedCamera, setSelectedCamera] = useState<string>('all');
  const [cameras, setCameras] = useState<any[]>([]);

  // Fetch analytics data
  useEffect(() => {
    fetchAnalytics();
  }, [timeRange, selectedCamera]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      
      // Fetch cameras for filter
      const camerasData = await apiService.getCameras();
      setCameras(camerasData);
      
      // Fetch detection stats
      const statsData = await apiService.getDetectionStats(
        selectedCamera === 'all' ? undefined : selectedCamera,
        timeRange
      );
      setStats(statsData);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    await fetchAnalytics();
  };

  const exportData = () => {
    if (!stats) return;
    
    const data = {
      timestamp: new Date().toISOString(),
      time_range: timeRange,
      camera_filter: selectedCamera,
      stats: stats
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getTopObjects = () => {
    if (!stats?.detections_by_class) return [];
    return Object.entries(stats.detections_by_class)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([class_name, count]) => ({ class_name, count }));
  };

  const getChartData = () => {
    if (!stats?.hourly_detections) return [];
    return stats.hourly_detections.map(item => ({
      hour: item.hour,
      count: item.count
    }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600">Configure AI models and view detection analytics</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={refreshData}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={exportData}
            disabled={!stats}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filters:</span>
          </div>
          
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="1h">Last Hour</option>
            <option value="6h">Last 6 Hours</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>

          <select
            value={selectedCamera}
            onChange={(e) => setSelectedCamera(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Cameras</option>
            {cameras.map(camera => (
              <option key={camera.id} value={camera.id}>
                {camera.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Stats Overview */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      ) : stats ? (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Detections</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.total_detections}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-blue-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">People Detected</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {stats.detections_by_class?.person || 0}
                  </p>
                </div>
                <Users className="w-8 h-8 text-green-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Vehicles Detected</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {(stats.detections_by_class?.car || 0) + 
                     (stats.detections_by_class?.truck || 0) + 
                     (stats.detections_by_class?.bus || 0)}
                  </p>
                </div>
                <Car className="w-8 h-8 text-orange-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Time Range</p>
                  <p className="text-3xl font-bold text-gray-900">{timeRange}</p>
                </div>
                <Clock className="w-8 h-8 text-purple-500" />
              </div>
            </div>
          </div>

          {/* Top Objects */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Most Detected Objects</h3>
            <div className="space-y-3">
              {getTopObjects().map((obj, index) => (
                <div key={obj.class_name} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-gray-500 w-6">{index + 1}.</span>
                    <span className="text-sm font-medium text-gray-900 capitalize">{obj.class_name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${Math.min(100, (obj.count / stats.total_detections) * 100)}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-900 w-12 text-right">{obj.count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Hourly Activity */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Hourly Detection Activity</h3>
            <div className="space-y-2">
              {getChartData().map((item) => (
                <div key={item.hour} className="flex items-center gap-3">
                  <span className="text-xs font-medium text-gray-500 w-12">{item.hour}</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-4">
                    <div 
                      className="bg-green-500 h-4 rounded-full" 
                      style={{ width: `${Math.min(100, (item.count / Math.max(...getChartData().map(d => d.count))) * 100)}%` }}
                    ></div>
                  </div>
                  <span className="text-xs font-medium text-gray-900 w-8 text-right">{item.count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Object Classes Breakdown */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Object Classes Breakdown</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(stats.detections_by_class || {}).map(([class_name, count]) => (
                <div key={class_name} className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">{count}</div>
                  <div className="text-sm text-gray-600 capitalize">{class_name}</div>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <BarChart className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Analytics Data</h3>
          <p className="text-gray-600 mb-4">No detection data available for the selected time range.</p>
          <p className="text-sm text-gray-500">Make sure cameras are running and detections are being recorded.</p>
        </div>
      )}
    </div>
  );
};