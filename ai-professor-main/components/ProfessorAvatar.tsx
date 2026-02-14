
import React from 'react';

interface ProfessorAvatarProps {
  isSpeaking: boolean;
}

export const ProfessorAvatar: React.FC<ProfessorAvatarProps> = ({ isSpeaking }) => {
  return (
    <div className="relative w-64 h-64 md:w-80 md:h-80">
      <svg viewBox="0 0 200 200" className="w-full h-full">
        {/* Shadow */}
        <ellipse cx="100" cy="185" rx="70" ry="10" fill="#000" opacity="0.1" />
        {/* Body */}
        <rect x="50" y="140" width="100" height="50" rx="10" fill="#475569" />
        {/* Head */}
        <circle cx="100" cy="90" r="50" fill="#f1f5f9" />
        <path d="M 70 140 Q 100 160, 130 140" fill="#475569" stroke="#475569" strokeWidth="2" /> {/* Collar */}
        
        {/* Face features */}
        {/* Eyes */}
        <circle cx="85" cy="85" r="5" fill="#334155" />
        <circle cx="115" cy="85" r="5" fill="#334155" />
        {/* Eyebrows */}
        <path d="M 78 75 Q 85 70, 92 75" stroke="#64748b" fill="none" strokeWidth="3" strokeLinecap="round" />
        <path d="M 108 75 Q 115 70, 122 75" stroke="#64748b" fill="none" strokeWidth="3" strokeLinecap="round" />
        
        {/* Mouth */}
        <g transform="translate(100, 105)">
            <path d="M -15 0 Q 0 5, 15 0" stroke="#64748b" fill="none" strokeWidth="3" strokeLinecap="round" className={isSpeaking ? 'animate-talk' : ''}/>
        </g>
        
        {/* Hair */}
        <path d="M 60 60 Q 100 20, 140 60 L 140 50 Q 100 10, 60 50 Z" fill="#94a3b8" />
        <path d="M 50 90 C 40 70, 50 50, 60 60" fill="#94a3b8" />
        <path d="M 150 90 C 160 70, 150 50, 140 60" fill="#94a3b8" />
        
      </svg>
    </div>
  );
};
