import React from 'react';

export const Settings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600">Configure system settings and preferences</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl">⚙️</span>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">System Settings</h3>
          <p className="text-gray-600 mb-4">Settings interface is under development.</p>
          <p className="text-sm text-gray-500">This section will allow you to:</p>
          <ul className="text-sm text-gray-500 mt-2 space-y-1">
            <li>• Configure system preferences</li>
            <li>• Manage user accounts and permissions</li>
            <li>• Set up notifications and alerts</li>
            <li>• Configure API settings</li>
          </ul>
        </div>
      </div>
    </div>
  );
};