
import React from 'react';

interface ExplanationBubbleProps {
  text: string;
  error: string | null;
}

export const ExplanationBubble: React.FC<ExplanationBubbleProps> = ({ text, error }) => {
  return (
    <div className="relative bg-indigo-50 p-6 rounded-lg shadow-inner min-h-[100px] text-slate-700 leading-relaxed text-lg prose max-w-none">
      {/* Speech bubble pointer */}
      <div className="absolute top-1/2 -left-4 w-4 h-8 bg-indigo-50 transform -translate-y-1/2" style={{clipPath: 'polygon(100% 0, 0 50%, 100% 100%)'}}></div>

      {error ? (
        <div className="text-red-600">
          <p className="font-bold">Oh, dear...</p>
          <p>{error}</p>
        </div>
      ) : (
        <p style={{whiteSpace: 'pre-wrap'}}>{text}</p>
      )}
    </div>
  );
};
