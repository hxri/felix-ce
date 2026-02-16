'use client';

import { useRef, useState, useEffect } from 'react';

interface CaptureScreenProps {
  onCapture: (image: string) => void;
}

export default function CaptureScreen({ onCapture }: CaptureScreenProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [error, setError] = useState<string>('');
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [debugInfo, setDebugInfo] = useState<string>('');
  const [cameraStarted, setCameraStarted] = useState(false);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');

  const startCamera = async (mode: 'user' | 'environment' = facingMode) => {
    try {
      setError('');
      setDebugInfo('Requesting camera access...');
      setCameraStarted(true);
      
      // Stop existing stream if any
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: mode
        },
        audio: false
      });

      setDebugInfo(`Camera stream obtained. Video tracks: ${mediaStream.getVideoTracks().length}`);
      setStream(mediaStream);
      setFacingMode(mode);

      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
          setDebugInfo('Stream attached to video element');
          
          videoRef.current.onloadedmetadata = () => {
            setDebugInfo(`Video ready. Playing...`);
            videoRef.current?.play()
              .then(() => {
                setDebugInfo('Video playing successfully');
                setIsCameraActive(true);
              })
              .catch(err => {
                setError(`Failed to play: ${err.message}`);
                console.error('Play error:', err);
              });
          };
        } else {
          setError('Video element still not found after delay');
        }
      }, 200);
      
    } catch (err) {
      console.error('Camera error:', err);
      setCameraStarted(false);
      if (err instanceof DOMException) {
        if (err.name === 'NotAllowedError') {
          setError('❌ Camera permission denied. Please allow camera access.');
        } else if (err.name === 'NotFoundError') {
          setError('❌ No camera found on this device.');
        } else if (err.name === 'NotReadableError') {
          setError('❌ Camera is in use by another application.');
        } else {
          setError(`❌ Camera error: ${err.message}`);
        }
      } else if (err instanceof Error) {
        setError(`❌ Error: ${err.message}`);
      } else {
        setError('❌ Failed to access camera.');
      }
    }
  };

  const toggleCamera = async () => {
    const newMode = facingMode === 'user' ? 'environment' : 'user';
    await startCamera(newMode);
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => {
        track.stop();
      });
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
      setStream(null);
      setIsCameraActive(false);
      setCameraStarted(false);
      setDebugInfo('');
    }
  };

  const capturePhoto = () => {
    if (!canvasRef.current || !videoRef.current || !isCameraActive) {
      setError('Camera not ready for capture');
      return;
    }

    const ctx = canvasRef.current.getContext('2d');
    
    if (!ctx) {
      setError('Failed to get canvas context');
      return;
    }

    try {
      const video = videoRef.current;
      
      if (video.videoWidth === 0 || video.videoHeight === 0) {
        setError('Video dimensions not available');
        return;
      }

      canvasRef.current.width = video.videoWidth;
      canvasRef.current.height = video.videoHeight;

      setDebugInfo(`Capturing at ${canvasRef.current.width}x${canvasRef.current.height}`);

      ctx.drawImage(video, 0, 0);
      
      const imageData = canvasRef.current.toDataURL('image/jpeg', 0.95);
      
      setDebugInfo('Photo captured successfully');
      
      stopCamera();
      
      onCapture(imageData);
    } catch (err) {
      setError(`Failed to capture photo: ${err instanceof Error ? err.message : 'Unknown error'}`);
      console.error('Capture error:', err);
    }
  };

  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
        if (videoRef.current) {
          videoRef.current.srcObject = null;
        }
      }
    };
  }, [stream]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="w-full max-w-md">
        <h1 className="text-3xl font-bold text-white mb-2 text-center">
          📸 Capture Your Photo
        </h1>
        <p className="text-slate-400 text-center mb-8">
          Take a full-body photo for the best results
        </p>

        {error && (
          <div className="bg-red-900 text-red-100 p-4 rounded-lg mb-6 border border-red-700">
            <p className="font-semibold">⚠️ Error</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {debugInfo && (
          <div className="bg-blue-900 text-blue-100 p-2 rounded mb-4 text-xs">
            Debug: {debugInfo}
          </div>
        )}

        {/* VIDEO ELEMENT WITH CAMERA TOGGLE */}
        <div className={`relative mb-6 rounded-lg overflow-hidden border-4 shadow-lg ${
          cameraStarted ? 'border-blue-500 bg-black' : 'hidden'
        }`}>
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{ 
              width: '100%',
              aspectRatio: '9/16',
              objectFit: 'cover',
              display: 'block'
            }}
          />
          
          {/* CAMERA TOGGLE BUTTON - TOP RIGHT CORNER */}
          {cameraStarted && isCameraActive && (
            <button
              onClick={toggleCamera}
              className="absolute top-3 right-3 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-3 rounded-lg transition shadow-lg z-10"
              title={`Switch to ${facingMode === 'user' ? 'back' : 'front'} camera`}
            >
              🔄
            </button>
          )}
          
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="w-3/4 h-full border-2 border-dashed border-blue-400 opacity-30" />
          </div>
        </div>

        {/* CONTROLS */}
        {cameraStarted && isCameraActive && (
          <div className="flex gap-3 mb-4">
            <button
              onClick={capturePhoto}
              className="flex-1 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-bold py-3 px-6 rounded-lg transition"
            >
              📷 Capture
            </button>
            <button
              onClick={stopCamera}
              className="flex-1 bg-red-600 hover:bg-red-700 active:bg-red-800 text-white font-bold py-3 px-6 rounded-lg transition"
            >
              ✕ Cancel
            </button>
          </div>
        )}

        {cameraStarted && !isCameraActive && (
          <p className="text-slate-400 text-sm text-center mb-4 animate-pulse">
            ⏳ Initializing camera...
          </p>
        )}

        {!cameraStarted && (
          <button
            onClick={() => startCamera()}
            className="w-full bg-green-600 hover:bg-green-700 active:bg-green-800 text-white font-bold py-3 px-6 rounded-lg transition"
          >
            🎥 Start Camera
          </button>
        )}

        {cameraStarted && !isCameraActive && (
          <p className="text-slate-400 text-xs text-center">
            Positioning yourself in the center for best results
          </p>
        )}

        <canvas ref={canvasRef} className="hidden" />
      </div>
    </div>
  );
}