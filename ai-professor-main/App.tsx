import React, { useState } from 'react';
import { ProfessorAvatar } from './components/ProfessorAvatar';

// API Response Interfaces
interface ProfessorContent {
  definition: string;
  key_notes: string[];
  application: string;
}

interface ApiResponse {
  answer: ProfessorContent;
  video_id: string | null;
}

const App: React.FC = () => {
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [data, setData] = useState<ApiResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setIsLoading(true);
    setError(null);
    setData(null);

    try {
      // Fetching from the Python Backend
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // Requirement: Body must be { "question": "..." }
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        throw new Error('Professor is unavailable.');
      }

      const result: ApiResponse = await response.json();
      setData(result);
    } catch (err) {
      // User-friendly Error Handling
      console.error(err);
      setError("The Professor is currently offline. Please check back later.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      <header className="bg-white border-b border-slate-200 px-8 py-4 flex items-center gap-4 sticky top-0 z-50 shadow-sm">
        <img src="/logo.png" alt="University Logo" className="h-12 w-12 object-contain"
          onError={(e) => (e.currentTarget.src = '/vite.svg')} />
        <div>
          <h1 className="text-xl font-bold text-slate-800">AI Professor</h1>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8 flex flex-col gap-8">

        {/* Interaction Area */}
        <div className="flex flex-col items-center gap-6">
          <ProfessorAvatar isSpeaking={isLoading} />

          <form onSubmit={handleAsk} className="w-full max-w-xl flex flex-col gap-3">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question..."
              disabled={isLoading}
              className="w-full px-5 py-3 rounded-full border border-slate-300 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 outline-none shadow-sm text-lg"
            />
            <button
              type="submit"
              disabled={isLoading || !question.trim()}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 rounded-full transition-all disabled:opacity-50"
            >
              {isLoading ? 'Consulting Archives...' : 'Ask the Professor'}
            </button>
          </form>

          {error && (
            <div className="p-4 bg-red-100 text-red-700 rounded-lg text-sm font-medium">
              {error}
            </div>
          )}
        </div>

        {/* Results Display */}
        {data && (
          <div className="flex flex-col gap-8 animate-fadeIn pb-12">

            {/* 1. Visual Learning (YouTube) */}
            {data.video_id && (
              <div className="w-full aspect-video bg-black rounded-2xl overflow-hidden shadow-xl">
                <iframe
                  src={`https://www.youtube.com/embed/${data.video_id}`}
                  className="w-full h-full"
                  title="Lesson Video"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              </div>
            )}

            {/* 2. Definition */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100">
              <h2 className="text-2xl font-bold text-slate-800 mb-4">The Concept</h2>
              <p className="text-lg text-slate-700 leading-relaxed">
                {data.answer.definition}
              </p>
            </div>

            {/* 3. Cards Container for Notes & Applications */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

              {/* Key Notes Card */}
              <div className="bg-indigo-50 p-6 rounded-2xl border border-indigo-100">
                <h3 className="text-sm font-bold text-indigo-800 uppercase tracking-wider mb-4">Key Notes</h3>
                <ul className="space-y-2">
                  {data.answer.key_notes.map((note, i) => (
                    <li key={i} className="flex gap-2 text-indigo-900">
                      <span className="font-bold">•</span>
                      <span>{note}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Applications Card */}
              <div className="bg-emerald-50 p-6 rounded-2xl border border-emerald-100">
                <h3 className="text-sm font-bold text-emerald-800 uppercase tracking-wider mb-4">Real-World Application</h3>
                <p className="text-emerald-900 font-medium">
                  {data.answer.application}
                </p>
              </div>

            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default App;
