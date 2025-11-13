import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/Button';
import { AlertCircle, Play, Pause, RefreshCw, Filter } from 'lucide-react';
import { useWebSocket } from '../hooks/useWebSocket';

interface Detection {
  id: string;
  timestamp: string;
  camera_id: string;
  object_class: string;
  confidence: number;
  bbox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  object_id: string;
  speed?: number;
  direction?: string;
  color?: string;
}

interface ObjectCount {
  object_class: string;
  count: number;
  last_updated: string;
}

interface DetectionStats {
  total_detections: number;
  objects_by_class: ObjectCount[];
  average_confidence: number;
  detection_rate: number;
}

interface RealTimeDetectionProps {
  cameraId?: string;
  className?: string;
}

const OBJECT_COLORS: Record<string, string> = {
  person: 'bg-blue-500',
  car: 'bg-green-500',
  truck: 'bg-orange-500',
  bus: 'bg-purple-500',
  bicycle: 'bg-yellow-500',
  motorcycle: 'bg-red-500',
};

const CONFIDENCE_THRESHOLDS = {
  high: 0.9,
  medium: 0.7,
  low: 0.5,
};

export const RealTimeDetection: React.FC<RealTimeDetectionProps> = ({ 
  cameraId, 
  className = '' 
}) => {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [objectCounts, setObjectCounts] = useState<ObjectCount[]>([]);
  const [detectionStats, setDetectionStats] = useState<DetectionStats | null>(null);
  const [isLive, setIsLive] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [maxDetections, setMaxDetections] = useState(50);

  const { isConnected, subscribe, unsubscribe } = useWebSocket();

  // Handle new detection events
  const handleDetection = useCallback((data: any) => {
    if (!isLive) return;

    const detection: Detection = data;
    
    // Filter by camera if specified
    if (cameraId && detection.camera_id !== cameraId) return;
    
    // Filter by object class if specified
    if (filter !== 'all' && detection.object_class !== filter) return;

    setDetections(prev => {
      const newDetections = [detection, ...prev];
      // Keep only the most recent detections
      return newDetections.slice(0, maxDetections);
    });
  }, [cameraId, filter, isLive, maxDetections]);

  // Handle object count updates
  const handleObjectCounts = useCallback((data: any) => {
    if (cameraId && data.camera_id !== cameraId) return;
    setObjectCounts(data.data || []);
  }, [cameraId]);

  // Handle detection stats updates
  const handleStatsUpdate = useCallback((data: any) => {
    if (cameraId && data.camera_id !== cameraId) return;
    setDetectionStats(data.data);
  }, [cameraId]);

  // Subscribe to WebSocket events
  useEffect(() => {
    if (!isConnected) return;

    // Subscribe to detection events
    subscribe('detection', handleDetection);
    subscribe('object_counts', handleObjectCounts);
    subscribe('stats_update', handleStatsUpdate);

    return () => {
      unsubscribe('detection', handleDetection);
      unsubscribe('object_counts', handleObjectCounts);
      unsubscribe('stats_update', handleStatsUpdate);
    };
  }, [isConnected, subscribe, unsubscribe, handleDetection, handleObjectCounts, handleStatsUpdate]);

  // Request initial stats
  useEffect(() => {
    if (isConnected) {
      // Request initial object counts
      window.socket?.emit('get_object_counts', { camera_id: cameraId });
      
      // Request initial detection stats
      window.socket?.emit('get_detection_stats', { camera_id: cameraId });
    }
  }, [isConnected, cameraId]);

  const clearDetections = () => {
    setDetections([]);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= CONFIDENCE_THRESHOLDS.high) return 'text-green-600';
    if (confidence >= CONFIDENCE_THRESHOLDS.medium) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= CONFIDENCE_THRESHOLDS.high) return 'bg-green-100 text-green-800';
    if (confidence >= CONFIDENCE_THRESHOLDS.medium) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const filteredDetections = filter === 'all' 
    ? detections 
    : detections.filter(d => d.object_class === filter);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Real-Time Detection</span>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm font-normal">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-4">
            <Button
              onClick={() => setIsLive(!isLive)}
              variant={isLive ? 'destructive' : 'default'}
              size="sm"
            >
              {isLive ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
              {isLive ? 'Pause' : 'Resume'}
            </Button>
            
            <Button
              onClick={clearDetections}
              variant="outline"
              size="sm"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Clear
            </Button>

            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4" />
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="px-3 py-1 border rounded-md text-sm"
              >
                <option value="all">All Objects</option>
                <option value="person">Person</option>
                <option value="car">Car</option>
                <option value="truck">Truck</option>
                <option value="bus">Bus</option>
                <option value="bicycle">Bicycle</option>
                <option value="motorcycle">Motorcycle</option>
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <label className="text-sm">Max detections:</label>
              <input
                type="number"
                value={maxDetections}
                onChange={(e) => setMaxDetections(parseInt(e.target.value) || 50)}
                className="w-16 px-2 py-1 border rounded-md text-sm"
                min="10"
                max="200"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detection Statistics */}
      {detectionStats && (
        <Card>
          <CardHeader>
            <CardTitle>Detection Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {detectionStats.total_detections}
                </div>
                <div className="text-sm text-gray-600">Total Detections</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {(detectionStats.average_confidence * 100).toFixed(1)}%
                </div>
                <div className="text-sm text-gray-600">Avg Confidence</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {detectionStats.detection_rate.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600">Detections/Min</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {detectionStats.objects_by_class.length}
                </div>
                <div className="text-sm text-gray-600">Object Types</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Object Counts */}
      {objectCounts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Object Counts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {objectCounts.map((count) => (
                <div key={count.object_class} className="text-center">
                  <div className={`w-12 h-12 mx-auto mb-2 rounded-full flex items-center justify-center text-white ${OBJECT_COLORS[count.object_class] || 'bg-gray-500'}`}>
                    <span className="text-lg font-bold">{count.count}</span>
                  </div>
                  <div className="text-sm font-medium capitalize">{count.object_class}</div>
                  <div className="text-xs text-gray-500">
                    {new Date(count.last_updated).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Detections */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Recent Detections ({filteredDetections.length})</span>
            {!isLive && (
              <Badge variant="secondary" className="ml-2">
                <AlertCircle className="w-3 h-3 mr-1" />
                Paused
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {filteredDetections.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                {isLive ? 'No detections yet. Waiting for objects...' : 'Detection paused'}
              </div>
            ) : (
              filteredDetections.map((detection) => (
                <div
                  key={detection.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${OBJECT_COLORS[detection.object_class] || 'bg-gray-500'}`} />
                    <div>
                      <div className="font-medium capitalize">{detection.object_class}</div>
                      <div className="text-sm text-gray-600">
                        {new Date(detection.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4 text-sm">
                    <Badge className={getConfidenceBadge(detection.confidence)}>
                      {(detection.confidence * 100).toFixed(1)}%
                    </Badge>
                    
                    {detection.speed && (
                      <div className="text-gray-600">
                        {detection.speed.toFixed(1)} km/h
                      </div>
                    )}
                    
                    {detection.direction && (
                      <div className="text-gray-600 capitalize">
                        {detection.direction}
                      </div>
                    )}
                    
                    {detection.color && (
                      <div className="flex items-center space-x-1">
                        <div 
                          className="w-3 h-3 rounded-full border"
                          style={{ backgroundColor: detection.color }}
                        />
                        <span className="text-gray-600 capitalize">{detection.color}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};