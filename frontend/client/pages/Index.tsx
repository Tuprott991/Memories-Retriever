import { Link } from "react-router-dom";
import BrainLogo from "../components/BrainLogo";

export default function Index() {
  return (
    <div className="min-h-screen bg-gradient-memory flex flex-col items-center justify-center px-4 overflow-hidden relative">
      {/* Decorative gradient elements */}
      <div className="absolute top-0 left-0 w-full h-full opacity-30 pointer-events-none">
        <div className="absolute top-20 left-20 w-64 h-64 bg-purple rounded-full filter blur-3xl opacity-20"></div>
        <div className="absolute bottom-20 right-20 w-72 h-72 bg-cyan rounded-full filter blur-3xl opacity-10"></div>
      </div>

      <div className="relative z-10 text-center space-y-12">
        {/* Logo/Icon */}
        <div className="flex justify-center animate-scale-in">
          <BrainLogo size="lg" className="animate-float" />
        </div>

        {/* Title */}
        <div className="space-y-4 animate-fade-in animate-delay-100">
          <h1 className="text-5xl md:text-6xl font-light text-white tracking-wide">
            Memory Retriever x LongMatrix
          </h1>
          <p className="text-gray-400 text-sm md:text-base max-w-md mx-auto">
            A compassionate companion for cherished memories
          </p>
        </div>

        {/* Buttons */}
        <div className="flex flex-col sm:flex-row gap-6 pt-8 w-full max-w-2xl mx-auto animate-fade-in animate-delay-200">
          <Link
            to="/palace"
            className="flex-1 aspect-square flex flex-col items-center justify-center gap-4 border-2 border-dashed border-cyan text-white font-medium rounded-lg hover:bg-cyan/10 hover:border-solid hover:shadow-lg hover:shadow-cyan/20 transition-all duration-300 p-8 group transform hover:scale-105"
          >
            <div className="text-4xl group-hover:scale-110 transition-transform">🧠</div>
            <span className="text-lg">Your Memory Companion</span>
            <p className="text-xs text-gray-400 text-center">Memory healing with AI</p>
          </Link>
          <Link
            to="/family-hub"
            className="flex-1 aspect-square flex flex-col items-center justify-center gap-4 border-2 border-dashed border-purple text-white font-medium rounded-lg hover:bg-purple/10 hover:border-solid hover:shadow-lg hover:shadow-purple/20 transition-all duration-300 p-8 group transform hover:scale-105"
          >
            <div className="text-4xl group-hover:scale-110 transition-transform">📚</div>
            <span className="text-lg">Family Archive</span>
            <p className="text-xs text-gray-400 text-center">Upload and organize memories</p>
          </Link>
        </div>

        {/* Subtle hint text */}
        <p className="text-gray-500 text-xs pt-8 animate-fade-in animate-delay-300">
          Step into your memories, or help us preserve them
        </p>
      </div>
    </div>
  );
}
