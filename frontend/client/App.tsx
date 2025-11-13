import "./global.css";

import { Toaster } from "@/components/ui/toaster";
import { createRoot } from "react-dom/client";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { lazy, Suspense } from "react";
import { AnimatePresence, motion } from "framer-motion";

// Lazy load pages for better performance
const Index = lazy(() => import("./pages/Index"));
const NotFound = lazy(() => import("./pages/NotFound"));
const MemoryPalace = lazy(() => import("./pages/MemoryPalace"));
const FamilyHub = lazy(() => import("./pages/FamilyHub"));

const queryClient = new QueryClient();

// Loading component
const PageLoader = () => (
  <div className="min-h-screen bg-gradient-memory flex items-center justify-center">
    <div className="text-center space-y-4">
      <div className="relative w-16 h-16 mx-auto">
        <div className="absolute inset-0 border-4 border-purple/30 border-t-purple rounded-full animate-spin"></div>
      </div>
      <p className="text-gray-400 text-sm">Loading...</p>
    </div>
  </div>
);

// Animated routes wrapper
const AnimatedRoutes = () => {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
      >
        <Routes location={location}>
          <Route path="/" element={<Index />} />
          <Route path="/palace" element={<MemoryPalace />} />
          <Route path="/family-hub" element={<FamilyHub />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </motion.div>
    </AnimatePresence>
  );
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Suspense fallback={<PageLoader />}>
          <AnimatedRoutes />
        </Suspense>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

createRoot(document.getElementById("root")!).render(<App />);
