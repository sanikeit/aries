import React from 'react';
import { AlertTriangle, Clock, Camera } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

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

interface AlertCardProps {
  alert: Alert;
  detailed?: boolean;
}

export const AlertCard: React.FC<AlertCardProps> = ({ alert, detailed = false }) => {
  const getAlertIcon = (alertType: string) => {
    switch (alertType) {
      case 'zone_entry':
      case 'zone_exit':
        return '🚶';
      case 'object_detected':
        return '👁️';
      case 'overcrowd':
        return '👥';
      default:
        return '⚠️';
    }
  };

  const getAlertColor = (alertType: string) => {
    switch (alertType) {
      case 'zone_entry':
      case 'zone_exit':
        return 'border-blue-200 bg-blue-50';
      case 'object_detected':
        return 'border-green-200 bg-green-50';
      case 'overcrowd':
        return 'border-red-200 bg-red-50';
      default:
        return 'border-yellow-200 bg-yellow-50';
    }
  };

  const formatAlertType = (alertType: string) => {
    return alertType
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const timeAgo = formatDistanceToNow(new Date(alert.timestamp), { addSuffix: true });

  return (
    <div className={`border rounded-lg p-4 ${getAlertColor(alert.alert_type)}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="text-2xl">
            {getAlertIcon(alert.alert_type)}
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-medium text-gray-900">
                {formatAlertType(alert.alert_type)}
              </h3>
              <span className="text-xs text-gray-500">
                {alert.camera_id}
              </span>
            </div>
            
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                <span>{timeAgo}</span>
              </div>
              <div className="flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                <span>{(alert.confidence * 100).toFixed(1)}% confidence</span>
              </div>
              <div className="flex items-center gap-1">
                <Camera className="w-3 h-3" />
                <span>{alert.object_class}</span>
              </div>
            </div>

            {detailed && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Object ID:</span>
                    <span className="ml-2 font-mono">{alert.object_id || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Bounding Box:</span>
                    <span className="ml-2 font-mono">
                      {alert.bbox.x.toFixed(0)},{alert.bbox.y.toFixed(0)} 
                      {alert.bbox.width.toFixed(0)}×{alert.bbox.height.toFixed(0)}
                    </span>
                  </div>
                </div>
                
                {alert.metadata && (
                  <div className="mt-2">
                    <span className="text-gray-500">Metadata:</span>
                    <pre className="mt-1 text-xs bg-gray-100 p-2 rounded overflow-auto">
                      {JSON.stringify(alert.metadata, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-1">
          <span className={`text-xs px-2 py-1 rounded-full ${
            alert.confidence > 0.8 
              ? 'bg-red-100 text-red-800' 
              : alert.confidence > 0.6 
              ? 'bg-orange-100 text-orange-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {alert.confidence > 0.8 ? 'High' : alert.confidence > 0.6 ? 'Medium' : 'Low'}
          </span>
        </div>
      </div>
    </div>
  );
};