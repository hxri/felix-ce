export default function LoadingScreen() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="text-center">
        <div className="mb-6">
          <div className="w-16 h-16 border-4 border-blue-300 border-t-blue-600 rounded-full animate-spin mx-auto" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Generating Your Content</h2>
        <p className="text-slate-400">Creating your photorealistic portrait...</p>
        <p className="text-slate-500 text-sm mt-4">This may take a few moments</p>
      </div>
    </div>
  );
}