import React, { useState, useEffect } from 'react';
import { apiService, Camera } from '../services/api';
import { 
  Camera as CameraIcon, 
  Plus, 
  Edit, 
  Trash2, 
  Play, 
  Pause, 
  RefreshCw,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react';

export const Cameras: React.FC = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingCamera, setEditingCamera] = useState<Camera | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    rtsp_uri: '',
    description: '',
    location: '',
  });
  const [submitting, setSubmitting] = useState(false);

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
    } catch (error) {
      console.error('Error fetching cameras:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      if (editingCamera) {
        // Update existing camera
        const updatedCamera = await apiService.updateCamera(editingCamera.id.toString(), formData);
        setCameras(cameras.map(cam => 
          cam.id === editingCamera.id 
            ? { ...updatedCamera, status: (updatedCamera.is_active ? 'online' : 'offline') as 'online' | 'offline' | 'error' }
            : cam
        ));
      } else {
        // Create new camera
        const newCamera = await apiService.createCamera(formData);
        setCameras([...cameras, { ...newCamera, status: (newCamera.is_active ? 'online' : 'offline') as 'online' | 'offline' | 'error' }]);
      }

      // Reset form and close modal
      setFormData({ name: '', rtsp_uri: '', description: '', location: '' });
      setShowAddModal(false);
      setEditingCamera(null);
    } catch (error) {
      console.error('Error saving camera:', error);
      alert('Failed to save camera. Please check the RTSP URI and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (camera: Camera) => {
    setEditingCamera(camera);
    setFormData({
      name: camera.name,
      rtsp_uri: camera.rtsp_uri,
      description: camera.description || '',
      location: camera.location || '',
    });
    setShowAddModal(true);
  };

  const handleDelete = async (cameraId: string) => {
    if (window.confirm('Are you sure you want to delete this camera? This action cannot be undone.')) {
      try {
        await apiService.deleteCamera(cameraId.toString());
        setCameras(cameras.filter(cam => cam.id !== cameraId));
      } catch (error) {
        console.error('Error deleting camera:', error);
        alert('Failed to delete camera. Please try again.');
      }
    }
  };

  const toggleCameraStatus = async (camera: Camera) => {
    try {
      const updatedCamera = await apiService.updateCamera(camera.id.toString(), {
        is_active: !camera.is_active
      });
      setCameras(cameras.map(cam => 
        cam.id === camera.id 
          ? { ...updatedCamera, status: (updatedCamera.is_active ? 'online' : 'offline') as 'online' | 'offline' | 'error' }
          : cam
      ));
    } catch (error) {
      console.error('Error updating camera status:', error);
      alert('Failed to update camera status. Please try again.');
    }
  };

  const closeModal = () => {
    setShowAddModal(false);
    setEditingCamera(null);
    setFormData({ name: '', rtsp_uri: '', description: '', location: '' });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'offline':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cameras</h1>
          <p className="text-gray-600">Manage your security cameras and stream configurations</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={fetchCameras}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <label className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 cursor-pointer">
            <input
              type="file"
              accept="video/*"
              className="hidden"
              onChange={async (e) => {
                const file = e.target.files?.[0]
                if (!file) return
                try {
                  const result = await apiService.uploadVideo(file)
                  await fetchCameras()
                  alert(`Uploaded. Stream URL: ${result.stream_url}`)
                } catch (err) {
                  console.error('Upload failed', err)
                  alert('Upload failed. Please try a different video file.')
                } finally {
                  e.currentTarget.value = ''
                }
              }}
            />
            Upload Video
          </label>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <Plus className="w-4 h-4" />
            Add Camera
          </button>
        </div>
      </div>

      {/* Cameras Grid */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading cameras...</p>
        </div>
      ) : cameras.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <CameraIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Cameras Configured</h3>
          <p className="text-gray-600 mb-4">Get started by adding your first security camera.</p>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 mx-auto"
          >
            <Plus className="w-4 h-4" />
            Add Camera
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cameras.map((camera) => (
            <div key={camera.id} className="bg-white rounded-lg shadow overflow-hidden">
              {/* Camera Preview */}
              <div className="aspect-video bg-black relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <CameraIcon className="w-16 h-16 text-gray-500 opacity-50" />
                </div>
                <div className="absolute top-2 left-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-sm">
                  {camera.name}
                </div>
                <div className="absolute top-2 right-2">
                  {getStatusIcon(camera.status)}
                </div>
              </div>

              {/* Camera Info */}
              <div className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">{camera.name}</h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    camera.status === 'online' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {camera.status}
                  </span>
                </div>
                
                {camera.description && (
                  <p className="text-sm text-gray-600 mb-3">{camera.description}</p>
                )}
                
                {camera.location && (
                  <p className="text-sm text-gray-500 mb-3">
                    <span className="font-medium">Location:</span> {camera.location}
                  </p>
                )}

                <div className="text-xs text-gray-500 mb-3">
                  Created: {new Date(camera.created_at).toLocaleDateString()}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={() => toggleCameraStatus(camera)}
                    className={`flex items-center gap-1 px-3 py-1 text-sm rounded-md ${
                      camera.is_active
                        ? 'bg-red-100 text-red-700 hover:bg-red-200'
                        : 'bg-green-100 text-green-700 hover:bg-green-200'
                    }`}
                  >
                    {camera.is_active ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                    {camera.is_active ? 'Stop' : 'Start'}
                  </button>
                  <button
                    onClick={() => handleEdit(camera)}
                    className="flex items-center gap-1 px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200"
                  >
                    <Edit className="w-3 h-3" />
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(camera.id)}
                    className="flex items-center gap-1 px-3 py-1 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200"
                  >
                    <Trash2 className="w-3 h-3" />
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              {editingCamera ? 'Edit Camera' : 'Add Camera'}
            </h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Camera Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Main Entrance"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  RTSP URI *
                </label>
                <input
                  type="text"
                  required
                  value={formData.rtsp_uri}
                  onChange={(e) => setFormData({ ...formData, rtsp_uri: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="rtsp://username:password@ip:port/stream"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Enter the RTSP stream URL for your camera
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={2}
                  placeholder="Brief description of the camera location or purpose"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Building A, Front Door"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={closeModal}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? 'Saving...' : (editingCamera ? 'Update' : 'Add Camera')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
