'use client';

interface GenderScreenProps {
  onSelect: (gender: 'male' | 'female') => void;
}

export default function GenderScreen({ onSelect }: GenderScreenProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-white mb-2 text-center">
          👤 Select Style
        </h1>
        <p className="text-slate-400 text-center mb-8">
          Choose to see outfit recommendations
        </p>

        <div className="space-y-4">
          <button
            onClick={() => onSelect('male')}
            className="w-full p-6 rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold text-lg transition transform hover:scale-105 active:scale-95"
          >
            <span className="text-4xl block mb-2">👨</span>
            Menswear
          </button>

          <button
            onClick={() => onSelect('female')}
            className="w-full p-6 rounded-lg bg-gradient-to-r from-pink-600 to-pink-700 hover:from-pink-700 hover:to-pink-800 text-white font-bold text-lg transition transform hover:scale-105 active:scale-95"
          >
            <span className="text-4xl block mb-2">👩</span>
            Womenswear
          </button>
        </div>

        <p className="text-slate-500 text-xs text-center mt-8">
          This helps us show relevant outfit options
        </p>
      </div>
    </div>
  );
}