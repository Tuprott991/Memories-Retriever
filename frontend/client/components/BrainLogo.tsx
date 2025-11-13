interface BrainLogoProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

export default function BrainLogo({ size = "md", className = "" }: BrainLogoProps) {
  const sizeClasses = {
    sm: "w-8 h-8",
    md: "w-16 h-16",
    lg: "w-20 h-20",
  };

  const iconSizes = {
    sm: "w-5 h-5",
    md: "w-8 h-8",
    lg: "w-10 h-10",
  };

  return (
    <div className={`relative ${sizeClasses[size]} ${className}`}>
      {/* Outer glow ring - AI processing effect */}
      <div className="absolute inset-0 rounded-full border-2 border-purple/30 bg-gradient-to-br from-purple/20 via-cyan/10 to-magenta/20 animate-pulse"></div>
      
      {/* Middle ring - Neural network layer */}
      <div className="absolute inset-[6px] rounded-full border border-cyan/40 bg-gradient-to-tr from-purple/10 to-transparent"></div>
      
      {/* Inner core */}
      <div className="absolute inset-[10px] rounded-full bg-gradient-to-br from-purple/30 via-cyan/20 to-purple/30 backdrop-blur-sm flex items-center justify-center">
        {/* Brain SVG with search/retrieval icon */}
        <div className={`${iconSizes[size]} relative`}>
          {/* Brain icon */}
          <svg
            className="absolute inset-0 text-purple drop-shadow-lg"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            {/* Brain structure - simplified neural pathways */}
            <path d="M12 2C10 2 8.5 3 7.5 4.5C6.5 3.5 5 3 3.5 4.5C2 6 2 8 2.5 9.5C2 11 2.5 13 4 14C3.5 15.5 4 17.5 5.5 18.5C7 19.5 8.5 19.5 10 19C10.5 20 11 21 12 21C13 21 13.5 20 14 19C15.5 19.5 17 19.5 18.5 18.5C20 17.5 20.5 15.5 20 14C21.5 13 22 11 21.5 9.5C22 8 22 6 20.5 4.5C19 3 17.5 3.5 16.5 4.5C15.5 3 14 2 12 2M12 4C13 4 13.5 4.5 14 5.5C13.5 6 13.5 7 14 8C14.5 8.5 15 8.5 15.5 8C16 7.5 16.5 7 17 7.5C17.5 8 18 8.5 18 9.5C17.5 10 17 10.5 17 11.5C17 12 17.5 12.5 18 12.5C18.5 12.5 19 13 19 13.5C19 14.5 18.5 15 18 15.5C17.5 16 17 16 16.5 16.5C16 17 16 17.5 16 18.5C15.5 18.5 15 18.5 14.5 18C14 17.5 13.5 17 13 17C12.5 17 12 17.5 11.5 18C11 18.5 10.5 18.5 10 18.5C10 17.5 10 17 9.5 16.5C9 16 8.5 16 8 15.5C7.5 15 7 14.5 7 13.5C7 13 7.5 12.5 8 12.5C8.5 12.5 9 12 9 11.5C9 10.5 8.5 10 8 9.5C8 8.5 8.5 8 9 7.5C9.5 7 10 7.5 10.5 8C11 8.5 11.5 8.5 12 8C12.5 7 12.5 6 12 5.5C11.5 4.5 11 4 12 4Z" />
          </svg>
          
          {/* Search/Magnifying glass overlay - represents retrieval */}
          <div className="absolute -bottom-1 -right-1 w-3 h-3 rounded-full bg-gradient-to-br from-cyan to-teal flex items-center justify-center border border-cyan/50 shadow-lg shadow-cyan/50">
            <svg
              className="w-2 h-2 text-white"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              viewBox="0 0 24 24"
            >
              <circle cx="11" cy="11" r="7" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
          </div>

          {/* Neural connection dots - AI nodes */}
          <div className="absolute -top-0.5 left-1/2 w-1 h-1 rounded-full bg-cyan animate-ping"></div>
          <div className="absolute top-1/2 -right-0.5 w-1 h-1 rounded-full bg-magenta animate-ping" style={{ animationDelay: "0.3s" }}></div>
          <div className="absolute -bottom-0.5 left-1/3 w-1 h-1 rounded-full bg-purple animate-ping" style={{ animationDelay: "0.6s" }}></div>
        </div>
      </div>

      {/* Scanning line effect - AI processing */}
      <div className="absolute inset-0 rounded-full overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan to-transparent animate-scan"></div>
      </div>
    </div>
  );
}
