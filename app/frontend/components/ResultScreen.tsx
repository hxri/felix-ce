'use client';

import { useState } from 'react';

interface ResultScreenProps {
  video: string;
  onRestart: () => void;
}

export default function ResultScreen({ video, onRestart }: ResultScreenProps) {
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string>('');

  const videoUrl = video;

  const handleSave = async () => {
    setIsSaving(true);
    setError('');
    try {
      console.log('Downloading from FAL:', videoUrl);
      const response = await fetch(videoUrl, {
        mode: 'cors',
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch video: ${response.status}`);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `apparel-showcase-${Date.now()}.mp4`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Save failed:', error);
      setError(`Failed to save video: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-white mb-6 text-center">✨ Your Video</h1>

        {error && (
          <div className="bg-red-900 text-red-100 p-4 rounded-lg mb-4 border border-red-700">
            <p className="text-sm">{error}</p>
          </div>
        )}

        <video
          src={videoUrl}
          controls
          autoPlay
          loop
          className="w-full rounded-lg mb-6 bg-black aspect-[9/16] object-cover"
          onError={(e) => {
            console.error('Video load error:', e);
            console.error('Tried to load from:', videoUrl);
            setError('Failed to load video from FAL CDN');
          }}
          onLoadedData={() => {
            console.log('Video loaded successfully from:', videoUrl);
          }}
        />

        <div className="space-y-3">
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="w-full bg-green-600 hover:bg-green-700 disabled:bg-slate-600 text-white font-bold py-3 px-6 rounded-lg transition"
          >
            {isSaving ? '💾 Saving...' : '💾 Save Video'}
          </button>

          <button
            onClick={onRestart}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition"
          >
            🔄 Start Over
          </button>
        </div>

        <p className="text-slate-400 text-sm text-center mt-6">
          Your video was generated using AI. Share it with friends!
        </p>

        <p className="text-slate-500 text-xs text-center mt-2">
          Video hosted on FAL CDN
        </p>
      </div>
    </div>
  );
}