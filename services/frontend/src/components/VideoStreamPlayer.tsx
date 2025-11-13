import React, { useState, useEffect, useRef } from 'react';
import ReactPlayer from 'react-player';
import { AlertCircle, Play, Pause, Settings, Maximize, Volume2, VolumeX } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/Button';
import { Badge } from './ui/badge';

interface VideoStreamPlayerProps {
  cameraId: string;
  streamUrl?: string;
  title?: string;
  muted?: boolean;
  playing?: boolean;
  onError?: (error: any) => void;
  onPlay?: () => void;
  onPause?: () => void;
  className?: string;
  showControls?: boolean;
  showStatus?: boolean;
  autoRetry?: boolean;
  maxRetries?: number;
}

interface StreamStatus {
  connected: boolean;
  status: string;
  fps: number;
  resolution: string;
  frame_count: number;
  error_count: number;
  last_frame_time: string;
}

export const VideoStreamPlayer: React.FC<VideoStreamPlayerProps> = ({
  cameraId,
  streamUrl,
  title = `Camera ${cameraId}`,
  muted = true,
  playing = true,
  onError,
  onPlay,
  onPause,
  className = '',
  showControls = true,
  showStatus = true,
  autoRetry = true,
  maxRetries = 3
}) => {
  const playerRef = useRef<ReactPlayer>(null);
  const [isPlaying, setIsPlaying] = useState(playing);
  const [isMuted, setIsMuted] = useState(muted);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [streamStatus, setStreamStatus] = useState<StreamStatus | null>(null);
  const [volume, setVolume] = useState(muted ? 0 : 0.5);
  const [showVolumeSlider, setShowVolumeSlider] = useState(false);

  // Determine the actual stream URL
  const getStreamUrl = () => {
    if (streamUrl) return streamUrl;
    
    // Default to HLS stream endpoint
    return `http://localhost:8000/streams/${cameraId}/hls.m3u8`;
  };

  const actualStreamUrl = getStreamUrl();

  // Fetch stream status
  useEffect(() => {
    const fetchStreamStatus = async () => {
      try {
        const response = await fetch(`http://localhost:8000/streams/${cameraId}/status`);
        if (response.ok) {
          const status = await response.json();
          setStreamStatus(status);
        }
      } catch (err) {
        console.warn('Failed to fetch stream status:', err);
      }
    };

    const interval = setInterval(fetchStreamStatus, 5000); // Update every 5 seconds
    fetchStreamStatus(); // Initial fetch

    return () => clearInterval(interval);
  }, [cameraId]);

  const handlePlay = () => {
    setIsPlaying(true);
    setError(null);
    setRetryCount(0);
    onPlay?.();
  };

  const handlePause = () => {
    setIsPlaying(false);
    onPause?.();
  };

  const handleError = (error: any) => {
    console.error('Video stream error:', error);
    setError('Failed to load stream');
    setIsLoading(false);
    onError?.(error);

    // Auto-retry logic
    if (autoRetry && retryCount < maxRetries) {
      setTimeout(() => {
        setRetryCount(prev => prev + 1);
        setIsPlaying(true);
        setError(null);
      }, 3000 * (retryCount + 1)); // Exponential backoff
    }
  };

  const handleReady = () => {
    setIsLoading(false);
    setError(null);
  };

  const toggleMute = () => {
    const newMuted = !isMuted;
    setIsMuted(newMuted);
    setVolume(newMuted ? 0 : 0.5);
  };

  const handleVolumeChange = (newVolume: number) => {
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const togglePlayPause = () => {
    if (isPlaying) {
      handlePause();
    } else {
      handlePlay();
    }
  };

  const getStatusColor = () => {
    if (error) return 'text-red-600';
    if (isLoading) return 'text-yellow-600';
    if (streamStatus?.connected) return 'text-green-600';
    return 'text-gray-600';
  };

  const getStatusText = () => {
    if (error) return 'Error';
    if (isLoading) return 'Loading...';
    if (streamStatus?.connected) return 'Connected';
    return 'Disconnected';
  };

  return (
    <Card className={`${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{title}</CardTitle>
          <div className="flex items-center space-x-2">
            {showStatus && (
              <div className={`flex items-center space-x-1 text-sm ${getStatusColor()}`}>
                <div className={`w-2 h-2 rounded-full ${
                  error ? 'bg-red-500' : 
                  isLoading ? 'bg-yellow-500' : 
                  streamStatus?.connected ? 'bg-green-500' : 'bg-gray-400'
                }`} />
                <span>{getStatusText()}</span>
              </div>
            )}
            {retryCount > 0 && (
              <Badge variant="secondary" className="text-xs">
                Retry {retryCount}/{maxRetries}
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        <div className="relative bg-black rounded-b-lg overflow-hidden">
          {/* Video Player */}
          <div className="relative aspect-video">
            {actualStreamUrl && (
              <ReactPlayer
                ref={playerRef}
                url={actualStreamUrl}
                playing={isPlaying}
                muted={isMuted}
                volume={volume}
                width="100%"
                height="100%"
                onPlay={handlePlay}
                onPause={handlePause}
                onError={handleError}
                onReady={handleReady}
                config={{
                  file: {
                    attributes: {
                      crossOrigin: 'anonymous'
                    },
                    hlsOptions: {
                      debug: false,
                      enableWorker: true,
                      lowLatencyMode: true,
                      backBufferLength: 30
                    }
                  }
                }}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0
                }}
              />
            )}

            {/* Loading Overlay */}
            {isLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
                <div className="text-white text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
                  <p>Loading stream...</p>
                </div>
              </div>
            )}

            {/* Error Overlay */}
            {error && (
              <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-75">
                <div className="text-white text-center p-4">
                  <AlertCircle className="w-12 h-12 mx-auto mb-2 text-red-400" />
                  <p className="text-lg font-semibold mb-1">Stream Error</p>
                  <p className="text-sm mb-3">{error}</p>
                  {autoRetry && retryCount < maxRetries && (
                    <p className="text-xs text-gray-300 mb-2">
                      Retrying in {3 * (retryCount + 1)} seconds...
                    </p>
                  )}
                  <Button
                    onClick={handlePlay}
                    size="sm"
                    variant="outline"
                    className="text-white border-white hover:bg-white hover:text-black"
                  >
                    Retry Now
                  </Button>
                </div>
              </div>
            )}

            {/* No Stream Overlay */}
            {!actualStreamUrl && !isLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
                <div className="text-white text-center p-4">
                  <AlertCircle className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                  <p className="text-lg font-semibold mb-1">No Stream Available</p>
                  <p className="text-sm">Stream URL not configured</p>
                </div>
              </div>
            )}
          </div>

          {/* Controls */}
          {showControls && actualStreamUrl && (
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/50 to-transparent p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {/* Play/Pause Button */}
                  <Button
                    onClick={togglePlayPause}
                    size="sm"
                    variant="ghost"
                    className="text-white hover:bg-white/20"
                  >
                    {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  </Button>

                  {/* Volume Control */}
                  <div className="flex items-center space-x-2">
                    <Button
                      onClick={toggleMute}
                      size="sm"
                      variant="ghost"
                      className="text-white hover:bg-white/20"
                    >
                      {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                    </Button>
                    
                    {showVolumeSlider && (
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={volume}
                        onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                        className="w-16 h-1 bg-white/30 rounded-lg appearance-none cursor-pointer"
                        onMouseLeave={() => setShowVolumeSlider(false)}
                      />
                    )}
                  </div>
                </div>

                {/* Stream Info */}
                {streamStatus && (
                  <div className="text-white text-xs space-y-1">
                    <div>{streamStatus.resolution} • {streamStatus.fps.toFixed(1)} FPS</div>
                    <div>Frames: {streamStatus.frame_count}</div>
                  </div>
                )}

                <div className="flex items-center space-x-2">
                  {/* Settings Button */}
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-white hover:bg-white/20"
                  >
                    <Settings className="w-4 h-4" />
                  </Button>

                  {/* Fullscreen Button */}
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-white hover:bg-white/20"
                  >
                    <Maximize className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Stream Status Details */}
        {showStatus && streamStatus && (
          <div className="p-3 bg-gray-50 text-xs text-gray-600">
            <div className="grid grid-cols-2 gap-2">
              <div>Status: <span className="font-medium">{streamStatus.status}</span></div>
              <div>Errors: <span className="font-medium">{streamStatus.error_count}</span></div>
              <div>Last Frame: <span className="font-medium">
                {new Date(streamStatus.last_frame_time).toLocaleTimeString()}
              </span></div>
              <div>Stream URL: <span className="font-medium truncate">{actualStreamUrl}</span></div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};