import React from 'react';

interface StatsCardProps {
  title: string;
  value: string | number;
  total?: number;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  bgColor: string;
}

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  total,
  icon: Icon,
  color,
  bgColor,
}) => {
  const percentage = total && typeof value === 'number' ? Math.round((value / total) * 100) : null;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <div className="flex items-baseline gap-2 mt-1">
            <p className="text-2xl font-semibold text-gray-900">{value}</p>
            {total && (
              <p className="text-sm text-gray-500">/ {total}</p>
            )}
          </div>
          {percentage && (
            <div className="mt-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${bgColor.replace('bg-', 'bg-')}`}
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-1">{percentage}% of total</p>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-full ${bgColor}`}>
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
      </div>
    </div>
  );
};