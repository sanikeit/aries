import React from 'react';
import ReactPlayer from 'react-player';
// import Hls from 'hls.js'; // Not currently used
import { useAuth } from '../contexts/AuthContext';

interface SecuredVideoPlayerProps {
  cameraId: string;
  width?: string;
  height?: string;
  muted?: boolean;
  playing?: boolean;
  onReady?: () => void;
  onError?: (error: any) => void;
}

export const SecuredVideoPlayer: React.FC<SecuredVideoPlayerProps> = ({
  cameraId,
  width = '100%',
  height = '100%',
  muted = true,
  playing = true,
  onReady,
  onError,
}) => {
  const { token } = useAuth();
  
  // Construct the HLS stream URL
  const streamUrl = `${window.location.protocol}//${window.location.hostname}:8000/streams/${cameraId}/index.m3u8`;
  
  // HLS.js configuration with authentication
  const hlsConfig = {
    xhrSetup: (xhr: XMLHttpRequest, url: string) => {
      // Set Authorization header for HLS requests
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }
      
      // Log for debugging
      console.log(`HLS request: ${url}`);
    },
    debug: false,
    enableWorker: true,
    lowLatencyMode: true,
    backBufferLength: 30,
  };

  const handlePlayerReady = (player: any) => {
    console.log('Player ready:', player);
    if (onReady) onReady();
  };

  const handlePlayerError = (error: any, data: any, hlsInstance: any, hlsGlobal: any) => {
    console.error('Player error:', error, data, hlsInstance, hlsGlobal);
    if (onError) onError(error);
  };

  return (
    <div className="relative w-full h-full bg-black rounded-lg overflow-hidden">
      <ReactPlayer
        url={streamUrl}
        width={width}
        height={height}
        muted={muted}
        playing={playing}
        config={{
          file: {
            hlsOptions: hlsConfig,
            hlsVersion: '1.4.12',
            forceHLS: true,
            forceSafariHLS: true,
          },
        }}
        onReady={handlePlayerReady}
        onError={handlePlayerError}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
        }}
      />
      
      {/* Loading overlay */}
      <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50">
        <div className="text-white text-sm">
          <div className="animate-pulse">Loading stream...</div>
        </div>
      </div>
      
      {/* Error overlay */}
      <div className="absolute inset-0 flex items-center justify-center bg-red-900 bg-opacity-75 hidden">
        <div className="text-white text-sm text-center">
          <div>Stream Error</div>
          <div className="text-xs mt-1">Please check camera connection</div>
        </div>
      </div>
    </div>
  );
};