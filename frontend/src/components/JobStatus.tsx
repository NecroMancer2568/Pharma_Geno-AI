import * as Progress from '@radix-ui/react-progress';

export default function JobStatus({ progress, currentStep }: { progress: number; currentStep: string }) {
  return (
    <div className="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow-sm border border-gray-100 text-center">
      <h2 className="text-2xl font-semibold mb-2 text-gray-800">Analyzing Genomic Data</h2>
      <p className="text-gray-500 mb-8 text-sm">Please wait while the AI pipeline processes the file. This may take up to 2 minutes.</p>
      
      <Progress.Root
        className="relative overflow-hidden bg-gray-200 rounded-full w-full h-4"
        value={progress}
      >
        <Progress.Indicator
          className="bg-blue-600 w-full h-full transition-transform duration-[500ms] ease-[cubic-bezier(0.65, 0, 0.35, 1)] rounded-full"
          style={{ transform: `translateX(-${100 - progress}%)` }}
        />
      </Progress.Root>
      
      <div className="flex justify-between items-center mt-4">
        <span className="text-sm font-medium text-blue-600">{currentStep}</span>
        <span className="text-sm font-medium text-gray-600">{progress}%</span>
      </div>
    </div>
  );
}