import React, { useState, useEffect } from 'react';
import { apiService, Camera } from '../services/api';
import { CameraStreamViewer } from '../components/CameraStreamViewer';
import { RealTimeDetection } from '../components/RealTimeDetection';
import { 
  Camera as CameraIcon, 
  Grid, 
  List,
  RefreshCw,
  AlertCircle
} from 'lucide-react';

export const LiveStreams: React.FC = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null);

  // Fetch cameras on component mount
  useEffect(() => {
    fetchCameras();
  }, []);

  const fetchCameras = async () => {
    try {
      setLoading(true);
      const camerasData = await apiService.getCameras();
      const camerasWithStatus = camerasData.map(camera => ({
        ...camera,
        status: (camera.is_active ? 'online' : 'offline') as 'online' | 'offline' | 'error'
      }));
      setCameras(camerasWithStatus);
      
      // Auto-select first online camera
      const firstOnline = camerasWithStatus.find(cam => cam.is_active);
      if (firstOnline && !selectedCamera) {
        setSelectedCamera(firstOnline);
      }
    } catch (error) {
      console.error('Error fetching cameras:', error);
    } finally {
      setLoading(false);
    }
  };

  const activeCameras = cameras.filter(camera => camera.is_active);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Live Streams</h1>
          <p className="text-gray-600">Real-time video feeds and object detection</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchCameras}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <div className="flex bg-gray-100 rounded-md p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`flex items-center gap-2 px-3 py-1 text-sm rounded ${
                viewMode === 'grid' 
                  ? 'bg-white text-gray-900 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Grid className="w-4 h-4" />
              Grid
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`flex items-center gap-2 px-3 py-1 text-sm rounded ${
                viewMode === 'list' 
                  ? 'bg-white text-gray-900 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <List className="w-4 h-4" />
              List
            </button>
          </div>
        </div>
      </div>

      {/* No Active Cameras Warning */}
      {activeCameras.length === 0 && !loading && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-yellow-600" />
            <div>
              <h3 className="text-sm font-medium text-yellow-800">No Active Cameras</h3>
              <p className="text-sm text-yellow-700 mt-1">
                You need to add and enable cameras to view live streams. 
                <a href="/cameras" className="text-yellow-800 font-medium hover:underline">
                  Go to Cameras page
                </a>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading cameras...</p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Camera Streams */}
          <div className="space-y-6">
            <h2 className="text-lg font-semibold text-gray-900">Video Streams</h2>
            {activeCameras.map((camera) => (
              <CameraStreamViewer
                key={camera.id}
                cameraId={camera.id}
                cameraName={camera.name}
                isActive={camera.is_active}
              />
            ))}
          </div>

          {/* Real-time Detection Panel */}
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Real-time Detection</h2>
              {selectedCamera && (
                <span className="text-sm text-gray-500">
                  Camera: {selectedCamera.name}
                </span>
              )}
            </div>
            <RealTimeDetection 
              cameraId={selectedCamera?.id.toString() || 'all'}
              limit={10}
            />
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {/* Single large stream view */}
          {selectedCamera && (
            <div className="bg-white rounded-lg shadow">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">{selectedCamera.name}</h2>
                <p className="text-sm text-gray-600">{selectedCamera.description}</p>
              </div>
              <CameraStreamViewer
                cameraId={selectedCamera.id}
                cameraName={selectedCamera.name}
                isActive={selectedCamera.is_active}
                className="border-0 shadow-none"
              />
            </div>
          )}

          {/* Camera List */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Camera List</h2>
            </div>
            <div className="divide-y divide-gray-200">
              {activeCameras.map((camera) => (
                <div
                  key={camera.id}
                  className={`p-4 cursor-pointer hover:bg-gray-50 ${
                    selectedCamera?.id === camera.id ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => setSelectedCamera(camera)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <CameraIcon className="w-5 h-5 text-gray-400" />
                      <div>
                        <h3 className="font-medium text-gray-900">{camera.name}</h3>
                        <p className="text-sm text-gray-600">{camera.location}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        camera.status === 'online' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {camera.status}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};