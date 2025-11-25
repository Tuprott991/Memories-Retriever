import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { Link } from "react-router-dom";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname,
    );
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-gradient-memory flex items-center justify-center px-4">
      <div className="text-center space-y-8">
        <div>
          <h1 className="text-6xl md:text-7xl font-light text-white mb-4">404</h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-2">
            Memory not found
          </p>
          <p className="text-gray-400">
            This path doesn't exist in your Memory Retriever x LORAN
          </p>
        </div>
        <Link
          to="/"
          className="inline-block px-8 py-3 border-2 border-purple text-white font-medium rounded-lg hover:bg-purple/10 transition-colors duration-300"
        >
          Return to Palace
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
