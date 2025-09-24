import React from 'react';

const ReportsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-secondary-900">Reports & Analytics</h1>
        <p className="text-secondary-600">Generate revenue reports and view analytics in Rands</p>
      </div>
      
      <div className="card">
        <div className="card-content">
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-secondary-900">Reports & Analytics</h3>
            <p className="text-secondary-500 mt-2">Generate revenue reports in Rands, export data, and view performance analytics</p>
            <p className="text-secondary-400 mt-1">Coming soon...</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;
