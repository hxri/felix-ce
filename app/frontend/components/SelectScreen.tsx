'use client';

import { useState } from 'react';
import Image from 'next/image';

interface SelectScreenProps {
  gender: 'male' | 'female';
  onSelect: (selections: { top: string; bottom: string; background: string }) => void;
}

const OUTFIT_TOPS_MALE = [
  { id: 1, name: 'Blue T-Shirt', image: 'https://i.postimg.cc/Xqs7H0wD/blue_tshirt.png' },
  { id: 2, name: 'White Polo', image: 'https://i.postimg.cc/wx2vTDSp/white_polo.png' },
  { id: 3, name: 'Black Hoodie', image: 'https://i.postimg.cc/59g0N8ZW/black_hoodie.png' },
  { id: 4, name: 'Formal Shirt', image: 'https://i.postimg.cc/Wz5bWPM7/formal_shirt.png' },
];

const OUTFIT_TOPS_FEMALE = [
  { id: 1, name: 'Pink Blouse', image: 'https://i.postimg.cc/B6GJ3b6b/pink_blouse.png' },
  { id: 2, name: 'White Tank', image: 'https://i.postimg.cc/JnWR80n7/white_tank.png' },
  { id: 3, name: 'Black Crop Top', image: 'https://i.postimg.cc/G21bRt2d/black_crop_top.png' },
  { id: 4, name: 'Formal Dress', image: 'https://i.postimg.cc/V6czwvNh/formal_dress.png' },
];

const OUTFIT_BOTTOMS_MALE = [
  { id: 1, name: 'Khaki Shorts', image: 'https://i.postimg.cc/hjHHKZKB/khaki_shorts.png' },
  { id: 2, name: 'Black Jeans', image: 'https://i.postimg.cc/wvSS949K/black_jeans.png' },
  { id: 3, name: 'Navy Chinos', image: 'https://i.postimg.cc/4drrX2XT/navy_chinos.png' },
  { id: 4, name: 'Running Shorts', image: 'https://i.postimg.cc/bJG7cfcx/running_shorts.png' },
];

const OUTFIT_BOTTOMS_FEMALE = [
  { id: 1, name: 'Denim Shorts', image: 'https://i.postimg.cc/LXMmS5sc/denim_shorts.png' },
  { id: 2, name: 'Black Skirt', image: 'https://i.postimg.cc/9Mjc20fS/black_skirt.png' },
  { id: 3, name: 'Casual Leggings', image: 'https://i.postimg.cc/V6czwvNH/casual_leggings.png' },
  { id: 4, name: 'Summer Dress', image: 'https://i.postimg.cc/0NS9hD9J/summer_dress.png' },
];

const BACKGROUNDS = [
  { id: 1, name: 'Urban Cafe', description: 'Modern outdoor coffee shop' },
  { id: 2, name: 'Office', description: 'Professional corporate environment' },
  { id: 3, name: 'Gym', description: 'Fitness studio setting' },
  { id: 4, name: 'Studio', description: 'Clean professional studio' },
];

export default function SelectScreen({ gender, onSelect }: SelectScreenProps) {
  const [selectedTop, setSelectedTop] = useState<string>('');
  const [selectedBottom, setSelectedBottom] = useState<string>('');
  const [selectedBg, setSelectedBg] = useState<string>('');
  const [step, setStep] = useState<'top' | 'bottom' | 'bg'>('top');

  const TOPS = gender === 'male' ? OUTFIT_TOPS_MALE : OUTFIT_TOPS_FEMALE;
  const BOTTOMS = gender === 'male' ? OUTFIT_BOTTOMS_MALE : OUTFIT_BOTTOMS_FEMALE;

  const handleNext = () => {
    if (step === 'top' && selectedTop) {
      setStep('bottom');
    } else if (step === 'bottom' && selectedBottom) {
      setStep('bg');
    } else if (step === 'bg' && selectedBg) {
      onSelect({
        top: selectedTop,
        bottom: selectedBottom,
        background: selectedBg
      });
    }
  };

  const canProceed = 
    (step === 'top' && selectedTop) ||
    (step === 'bottom' && selectedBottom) ||
    (step === 'bg' && selectedBg);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="w-full max-w-md">
        {/* Progress indicator */}
        <div className="flex gap-2 mb-6">
          <div className={`h-2 flex-1 rounded ${step === 'top' || step === 'bottom' || step === 'bg' ? 'bg-blue-600' : 'bg-slate-700'}`} />
          <div className={`h-2 flex-1 rounded ${step === 'bottom' || step === 'bg' ? 'bg-blue-600' : 'bg-slate-700'}`} />
          <div className={`h-2 flex-1 rounded ${step === 'bg' ? 'bg-blue-600' : 'bg-slate-700'}`} />
        </div>

        {step === 'top' && (
          <>
            <h2 className="text-2xl font-bold text-white mb-2">Select Top Wear</h2>
            <p className="text-slate-400 mb-6">Choose a {gender === 'male' ? 'shirt or top' : 'top or blouse'}</p>
            <div className="grid grid-cols-2 gap-4 mb-6">
              {TOPS.map(top => (
                <button
                  key={top.id}
                  onClick={() => setSelectedTop(top.name)}
                  className={`p-3 rounded-lg transition transform hover:scale-105 ${
                    selectedTop === top.name
                      ? 'ring-2 ring-blue-500 bg-blue-600/20'
                      : 'bg-slate-700 hover:bg-slate-600'
                  }`}
                >
                  <div className="w-full h-32 bg-slate-600 rounded mb-2 relative overflow-hidden">
                    <Image
                      src={top.image}
                      alt={top.name}
                      fill
                      className="object-cover"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  </div>
                  <p className="text-white text-sm font-semibold text-center">{top.name}</p>
                </button>
              ))}
            </div>
          </>
        )}

        {step === 'bottom' && (
          <>
            <h2 className="text-2xl font-bold text-white mb-2">Select Bottom Wear</h2>
            <p className="text-slate-400 mb-6">Choose {gender === 'male' ? 'pants or shorts' : 'skirt, pants or shorts'}</p>
            <div className="grid grid-cols-2 gap-4 mb-6">
              {BOTTOMS.map(bottom => (
                <button
                  key={bottom.id}
                  onClick={() => setSelectedBottom(bottom.name)}
                  className={`p-3 rounded-lg transition transform hover:scale-105 ${
                    selectedBottom === bottom.name
                      ? 'ring-2 ring-blue-500 bg-blue-600/20'
                      : 'bg-slate-700 hover:bg-slate-600'
                  }`}
                >
                  <div className="w-full h-32 bg-slate-600 rounded mb-2 relative overflow-hidden">
                    <Image
                      src={bottom.image}
                      alt={bottom.name}
                      fill
                      className="object-cover"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  </div>
                  <p className="text-white text-sm font-semibold text-center">{bottom.name}</p>
                </button>
              ))}
            </div>
          </>
        )}

        {step === 'bg' && (
          <>
            <h2 className="text-2xl font-bold text-white mb-2">Select Background</h2>
            <p className="text-slate-400 mb-6">Choose a setting</p>
            <div className="space-y-3 mb-6">
              {BACKGROUNDS.map(bg => (
                <button
                  key={bg.id}
                  onClick={() => setSelectedBg(bg.name)}
                  className={`w-full p-4 rounded-lg text-left transition transform hover:scale-105 ${
                    selectedBg === bg.name
                      ? 'ring-2 ring-blue-500 bg-blue-600'
                      : 'bg-slate-700 hover:bg-slate-600'
                  }`}
                >
                  <p className="text-white font-semibold">{bg.name}</p>
                  <p className="text-slate-300 text-sm">{bg.description}</p>
                </button>
              ))}
            </div>
          </>
        )}

        <button
          onClick={handleNext}
          disabled={!canProceed}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition"
        >
          {step === 'bg' && canProceed ? '✨ Generate' : 'Next →'}
        </button>
      </div>
    </div>
  );
}