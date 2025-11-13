import React, { useState, useRef, useEffect } from 'react';
import { Stage, Layer, Image, Line, Circle, Text } from 'react-konva';
import { Button } from './ui/Button';
import { Save, Trash2, Plus, Minus } from 'lucide-react';

interface Point {
  x: number;
  y: number;
}

interface ROIEditorProps {
  cameraId: string;
  jobId: number;
  imageUrl?: string;
  existingPoints?: Point[];
  onSave: (points: Point[]) => Promise<void>;
  onCancel: () => void;
}

export const ROIEditor: React.FC<ROIEditorProps> = ({
// cameraId,
  // jobId,
  imageUrl = 'https://trae-api-us.mchost.guru/api/ide/v1/text_to_image?prompt=security%20camera%20overhead%20view%20of%20parking%20lot%20with%20cars%20and%20pedestrians%2C%20surveillance%20style%2C%20high%20contrast&image_size=landscape_16_9',
  existingPoints = [],
  onSave,
  onCancel,
}) => {
  const [points, setPoints] = useState<Point[]>(existingPoints);
  const [selectedPoint, setSelectedPoint] = useState<number | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const stageRef = useRef<any>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);

  // Load background image
  useEffect(() => {
    const img: HTMLImageElement = document.createElement('img');
    img.src = imageUrl;
    img.onload = () => {
      setImage(img);
    };
    img.onerror = () => {
      console.error('Failed to load image');
    };
    imageRef.current = img;
  }, [imageUrl]);

  const handleStageClick = (e: any) => {
    if (!isDrawing) return;

    const pos = e.target.getStage().getPointerPosition();
    if (!pos) return;

    const newPoint: Point = { x: pos.x, y: pos.y };
    setPoints([...points, newPoint]);
  };

  const handlePointClick = (index: number) => {
    setSelectedPoint(index);
  };

  const handlePointDrag = (index: number, e: any) => {
    const newPoints = [...points];
    newPoints[index] = { x: e.target.x(), y: e.target.y() };
    setPoints(newPoints);
  };

  const addPoint = () => {
    if (points.length === 0) {
      // Add initial points in a rectangle
      setPoints([
        { x: 100, y: 100 },
        { x: 300, y: 100 },
        { x: 300, y: 300 },
        { x: 100, y: 300 },
      ]);
    } else {
      // Add point in the middle of the polygon
      const centerX = points.reduce((sum, p) => sum + p.x, 0) / points.length;
      const centerY = points.reduce((sum, p) => sum + p.y, 0) / points.length;
      setPoints([...points, { x: centerX, y: centerY }]);
    }
  };

  const removePoint = () => {
    if (selectedPoint !== null && points.length > 3) {
      const newPoints = points.filter((_, index) => index !== selectedPoint);
      setPoints(newPoints);
      setSelectedPoint(null);
    }
  };

  const clearPoints = () => {
    setPoints([]);
    setSelectedPoint(null);
  };

  const handleSave = async () => {
    if (points.length < 3) {
      alert('Please draw at least 3 points to create a valid polygon');
      return;
    }

    try {
      await onSave(points);
    } catch (error) {
      console.error('Failed to save ROI:', error);
      alert('Failed to save ROI configuration');
    }
  };

  const stageWidth = 800;
  const stageHeight = 450;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-800">ROI Editor</h2>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsDrawing(!isDrawing)}
            className={isDrawing ? 'bg-blue-100' : ''}
          >
            {isDrawing ? 'Stop Drawing' : 'Start Drawing'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={addPoint}
            disabled={isDrawing}
          >
            <Plus className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={removePoint}
            disabled={selectedPoint === null || points.length <= 3}
          >
            <Minus className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={clearPoints}
            disabled={points.length === 0}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="border rounded-lg overflow-hidden mb-4">
        <Stage
          ref={stageRef}
          width={stageWidth}
          height={stageHeight}
          onClick={handleStageClick}
          className="cursor-crosshair"
        >
          <Layer>
            {/* Background Image */}
            {image && (
              <Image
                image={image}
                width={stageWidth}
                height={stageHeight}
                opacity={0.7}
              />
            )}

            {/* ROI Polygon */}
            {points.length > 2 && (
              <Line
                points={points.flatMap(p => [p.x, p.y])}
                closed={true}
                fill="rgba(59, 130, 246, 0.3)"
                stroke="#3b82f6"
                strokeWidth={2}
              />
            )}

            {/* Control Points */}
            {points.map((point, index) => (
              <Circle
                key={index}
                x={point.x}
                y={point.y}
                radius={6}
                fill={selectedPoint === index ? '#ef4444' : '#3b82f6'}
                stroke="white"
                strokeWidth={2}
                draggable
                onClick={() => handlePointClick(index)}
                onDragEnd={(e) => handlePointDrag(index, e)}
                className="cursor-move"
              />
            ))}

            {/* Instructions */}
            {points.length === 0 && (
              <Text
                x={stageWidth / 2}
                y={stageHeight / 2}
                text="Click 'Start Drawing' and then click on the image to create ROI points"
                fontSize={16}
                fill="#6b7280"
                align="center"
                verticalAlign="middle"
                width={400}
                height={100}
                offsetX={200}
                offsetY={50}
              />
            )}
          </Layer>
        </Stage>
      </div>

      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-600">
          Points: {points.length} | 
          {isDrawing ? 'Click to add points' : 'Drag points to adjust'}
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={points.length < 3}>
            <Save className="w-4 h-4 mr-2" />
            Save ROI
          </Button>
        </div>
      </div>

      {selectedPoint !== null && (
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-800">
            Selected point {selectedPoint + 1}: ({points[selectedPoint]?.x.toFixed(0)}, {points[selectedPoint]?.y.toFixed(0)})
          </p>
          <p className="text-xs text-blue-600 mt-1">
            Drag the point to move it, or click the minus button to remove it
          </p>
        </div>
      )}
    </div>
  );
};