import React, { useState, useEffect } from 'react';
import { SecuredVideoPlayer } from './SecuredVideoPlayer';
import { apiService } from '../services/api';
import { Play, StopCircle, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';

interface CameraStreamViewerProps {
  cameraId: string;
  cameraName: string;
  isActive: boolean;
  className?: string;
}

export const CameraStreamViewer: React.FC<CameraStreamViewerProps> = ({
  cameraId,
  cameraName,
  isActive,
  className = ''
}) => {
  const [streamStatus, setStreamStatus] = useState<{
    stream_active: boolean;
    stream_url: string | null;
    camera_active: boolean;
  }>({ stream_active: false, stream_url: null, camera_active: isActive });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStreamStatus = async () => {
    try {
      const status = await apiService.getCameraStreamStatus(cameraId);
      setStreamStatus(status);
      setError(null);
    } catch (err) {
      console.error('Error fetching stream status:', err);
      setError('Failed to fetch stream status');
    }
  };

  const startStream = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.startCameraStream(cameraId);
      setStreamStatus(prev => ({
        ...prev,
        stream_active: true,
        stream_url: result.stream_url
      }));
    } catch (err) {
      console.error('Error starting stream:', err);
      setError('Failed to start stream');
    } finally {
      setLoading(false);
    }
  };

  const stopStream = async () => {
    setLoading(true);
    setError(null);
    try {
      await apiService.stopCameraStream(cameraId);
      setStreamStatus(prev => ({
        ...prev,
        stream_active: false,
        stream_url: null
      }));
    } catch (err) {
      console.error('Error stopping stream:', err);
      setError('Failed to stop stream');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStreamStatus();
    // Refresh status every 10 seconds
    const interval = setInterval(fetchStreamStatus, 10000);
    return () => clearInterval(interval);
  }, [cameraId]);

  const getStreamUrl = () => {
    if (streamStatus.stream_active && streamStatus.stream_url) {
      return `${window.location.origin}${streamStatus.stream_url}`;
    }
    return null;
  };

  return (
    <div className={`bg-white rounded-lg shadow ${className}`}>
      {/* Stream Header */}
      <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="font-medium text-gray-900">{cameraName}</h3>
          <div className="flex items-center gap-1">
            {streamStatus.stream_active ? (
              <CheckCircle className="w-4 h-4 text-green-500" />
            ) : (
              <AlertCircle className="w-4 h-4 text-gray-400" />
            )}
            <span className="text-xs text-gray-500">
              {streamStatus.stream_active ? 'Streaming' : 'Offline'}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchStreamStatus}
            disabled={loading}
            className="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-50"
            title="Refresh status"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          {streamStatus.stream_active ? (
            <button
              onClick={stopStream}
              disabled={loading || !isActive}
              className="flex items-center gap-1 px-3 py-1 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <StopCircle className="w-3 h-3" />
              Stop
            </button>
          ) : (
            <button
              onClick={startStream}
              disabled={loading || !isActive}
              className="flex items-center gap-1 px-3 py-1 text-sm bg-green-100 text-green-700 rounded-md hover:bg-green-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Play className="w-3 h-3" />
              Start
            </button>
          )}
        </div>
      </div>

      {/* Video Stream */}
      <div className="aspect-video bg-black relative">
        {getStreamUrl() ? (
          <SecuredVideoPlayer
            cameraId={cameraId}
            muted={true}
            playing={true}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-gray-400">
              <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">
                {isActive ? 'Stream not available' : 'Camera is disabled'}
              </p>
              <p className="text-xs mt-1">
                {isActive ? 'Click Start to begin streaming' : 'Enable camera to start streaming'}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="px-4 py-2 bg-red-50 border-t border-red-200">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}
    </div>
  );
};
