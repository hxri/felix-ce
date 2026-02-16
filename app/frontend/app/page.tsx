'use client';

import { useState } from 'react';
import CaptureScreen from '@/components/CaptureScreen';
import GenderScreen from '@/components/GenderScreen';
import SelectScreen from '@/components/SelectScreen';
import LoadingScreen from '@/components/LoadingScreen';
import ResultScreen from '@/components/ResultScreen';

type Step = 'capture' | 'gender' | 'select' | 'loading' | 'result';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function Home() {
  const [step, setStep] = useState<Step>('capture');
  const [gender, setGender] = useState<'male' | 'female'>('male');
  const [personImage, setPersonImage] = useState<string>('');
  const [selections, setSelections] = useState({
    top: '',
    bottom: '',
    background: ''
  });
  const [generatedVideo, setGeneratedVideo] = useState<string>('');
  const [loadingMessage, setLoadingMessage] = useState<string>('Generating your content...');

  const handleCapture = (image: string) => {
    setPersonImage(image);
    setStep('gender');
  };

  const handleGenderSelect = (selectedGender: 'male' | 'female') => {
    setGender(selectedGender);
    setStep('select');
  };

  const handleSelect = (selected: typeof selections) => {
    setSelections(selected);
    setStep('loading');
    generateContent(selected);
  };

  const generateContent = async (selected: typeof selections) => {
    try {
      setLoadingMessage('Creating photorealistic portrait...');
      
      console.log('API_BASE_URL:', API_BASE_URL);
      
      // Handle full dresses - if Formal Dress or Summer Dress is selected, use only that
      let outfit_top = selected.top;
      let outfit_bottom = selected.bottom;
      let apparel_type = `${outfit_top} with ${outfit_bottom}`;
      
      if (gender === 'female') {
        if (selected.top === 'Formal Dress') {
          outfit_bottom = '';
          apparel_type = 'Formal Dress';
        } else if (selected.bottom === 'Summer Dress') {
          outfit_top = '';
          apparel_type = 'Summer Dress';
        }
      }
      
      console.log('Generating with:', {
        gender: gender,
        outfit_top: outfit_top,
        outfit_bottom: outfit_bottom,
        apparel_type: apparel_type,
        background: selected.background
      });

      // Generate image
      const generateUrl = '/api/generate';
      console.log('POST to:', generateUrl);
      
      const imgRes = await fetch(generateUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          person_image: personImage,
          gender: gender,
          outfit_top: outfit_top,
          outfit_bottom: outfit_bottom,
          background: selected.background,
          environment: 'professional lighting, studio'
        })
      });

      console.log('Image generation response status:', imgRes.status);
      
      if (!imgRes.ok) {
        const errorData = await imgRes.json();
        console.error('Image generation error:', errorData);
        throw new Error(`Image generation failed: ${imgRes.status} - ${errorData.error || 'Unknown error'}`);
      }

      const imgJob = await imgRes.json();
      console.log('Image job ID:', imgJob.job_id);
      
      const imageFile = await pollJobStatus(imgJob.job_id, `${API_BASE_URL}/api/status`, 'Creating...');
      
      console.log('Generated image file:', imageFile);
      setLoadingMessage('Generating video animation...');

      // Generate video with gender parameter
      const videoUrl = '/api/video';
      console.log('POST to:', videoUrl);
      
      const vidRes = await fetch(videoUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_file: imageFile,
          gender: gender,
          outfit_top: selected.top,
          outfit_bottom: selected.bottom,
          motion_description: gender === 'male' 
            ? 'man stands still, turns around slowly 360 degrees to show full outfit, stands facing forward, confident posture, no adjusting clothes' 
            : 'woman stands still, turns around slowly 360 degrees to show full outfit, stands facing forward, elegant posture, keeps hands at sides, no touching or adjusting clothes, no lifting or moving fabric',
          model: 'grok',
          duration_sec: 4
        })
      });

      console.log('Video generation response status:', vidRes.status);
      
      if (!vidRes.ok) {
        const errorData = await vidRes.json();
        console.error('Video generation error:', errorData);
        throw new Error(`Video generation failed: ${vidRes.status} - ${errorData.error || 'Unknown error'}`);
      }

      const vidJob = await vidRes.json();
      console.log('Video job ID:', vidJob.job_id);
      
      const videoFile = await pollJobStatus(vidJob.job_id, `${API_BASE_URL}/api/video/status`, 'Rendering video...');

      console.log('Generated video file:', videoFile);
      setGeneratedVideo(videoFile);
      setStep('result');
    } catch (error) {
      console.error('Generation failed:', error);
      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setStep('select');
    }
  };

  const pollJobStatus = async (
    jobId: string,
    statusUrl: string,
    message: string
  ): Promise<string> => {
    let attempts = 0;
    const maxAttempts = 180;

    while (attempts < maxAttempts) {
      try {
        const url = `${statusUrl}/${jobId}`;
        console.log(`Polling: ${url} (attempt ${attempts + 1})`);
        
        const res = await fetch(url);
        const data = await res.json();

        console.log(`Job ${jobId} status:`, data.status);

        if (data.status === 'completed') {
          const fileUrl = data.image_file || data.video_file;
          console.log('Job completed, file:', fileUrl);
          return fileUrl;
        } else if (data.status === 'failed') {
          throw new Error(data.error || 'Job failed');
        }

        setLoadingMessage(`${message} (${attempts + 1}s)`);
        await new Promise(r => setTimeout(r, 1000));
        attempts++;
      } catch (error) {
        if (error instanceof Error && !error.message.includes('Job failed')) {
          await new Promise(r => setTimeout(r, 1000));
          attempts++;
        } else {
          throw error;
        }
      }
    }

    throw new Error('Generation timeout');
  };

  const handleRestart = () => {
    setStep('capture');
    setPersonImage('');
    setGeneratedVideo('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      {step === 'capture' && <CaptureScreen onCapture={handleCapture} />}
      {step === 'gender' && <GenderScreen onSelect={handleGenderSelect} />}
      {step === 'select' && <SelectScreen gender={gender} onSelect={handleSelect} />}
      {step === 'loading' && <LoadingScreen message={loadingMessage} />}
      {step === 'result' && (
        <ResultScreen 
          video={generatedVideo} 
          onRestart={handleRestart} 
        />
      )}
    </div>
  );
}