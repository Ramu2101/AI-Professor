
import React from 'react';

export const Loader: React.FC = () => {
  return (
    <div className="text-center p-4">
        <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-lg font-semibold text-slate-600 font-heading">The Professor is thinking...</p>
        <p className="text-slate-500">Preparing your explanation.</p>
    </div>
  );
};
