import { Link } from "react-router-dom";

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
        <div className="flex justify-center">
          <div className="w-16 h-16 rounded-full border-2 border-purple bg-purple/10 flex items-center justify-center">
            <div className="w-12 h-12 rounded-full border border-purple flex items-center justify-center">
              <svg
                className="w-6 h-6 text-purple"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Title */}
        <div className="space-y-4">
          <h1 className="text-5xl md:text-6xl font-light text-white tracking-wide">
            Memory Palace
          </h1>
          <p className="text-gray-400 text-sm md:text-base max-w-md mx-auto">
            A compassionate companion for cherished memories
          </p>
        </div>

        {/* Buttons */}
        <div className="flex flex-col gap-4 pt-8 w-full max-w-sm mx-auto">
          <Link
            to="/palace"
            className="px-8 py-3 border-2 border-cyan text-white font-medium rounded-lg hover:bg-cyan/10 transition-colors duration-300 text-center"
          >
            Enter Your Palace
          </Link>
          <Link
            to="/family-hub"
            className="px-8 py-3 border-2 border-purple text-white font-medium rounded-lg hover:bg-purple/10 transition-colors duration-300 text-center"
          >
            Family Hub
          </Link>
        </div>

        {/* Subtle hint text */}
        <p className="text-gray-500 text-xs pt-8">
          Step into your memories, or help us preserve them
        </p>
      </div>
    </div>
  );
}
