import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import { Send, UserCircle, X, Upload } from "lucide-react";
import BrainLogo from "../components/BrainLogo";
import { ourHomeMockData, MockMemoryData } from "../data/mockMemories";

interface JourneyCard {
  id: string;
  title: string;
  subtitle: string;
  icon: string;
  color: string;
}

interface MemoryItem {
  id: string;
  type: "photo" | "video";
  title: string;
  description: string;
  mediaUrl: string;
  timestamp?: string;
}

interface Message {
  role: string;
  content: string;
  memories?: MemoryItem[];
  currentMemoryIndex?: number;
}

const journeys: JourneyCard[] = [
  {
    id: "happy-times",
    title: "Happy Times",
    subtitle: "Joyful memories",
    icon: "😊",
    color: "from-teal/20 to-teal/5",
  },
  {
    id: "my-love",
    title: "My Love",
    subtitle: "Love and affection",
    icon: "❤️",
    color: "from-magenta/20 to-magenta/5",
  },
  {
    id: "children",
    title: "The Children",
    subtitle: "Moments from youth",
    icon: "👨‍👩‍👧‍👦",
    color: "from-amber-600/20 to-amber-600/5",
  },
  {
    id: "home",
    title: "Our Home",
    subtitle: "Home sweet home",
    icon: "🏡",
    color: "from-purple/20 to-purple/5",
  },
];

export default function MemoryPalace() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Welcome to your Memory Retriever x LORAN. What would you like to explore today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [viewingMemoryModal, setViewingMemoryModal] = useState<{
    memories: MemoryItem[];
    currentIndex: number;
    messageIndex: number;
  } | null>(null);
  const [reasoningModal, setReasoningModal] = useState<{
    visible: boolean;
    reasoning: string;
    paraphrasedQuery: string;
  } | null>(null);
  const [autoPlayingMemories, setAutoPlayingMemories] = useState<{
    memories: MemoryItem[];
    currentIndex: number;
    isPlaying: boolean;
  } | null>(null);
  const autoPlayTimerRef = useRef<NodeJS.Timeout | null>(null);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [profileData, setProfileData] = useState({
    name: "",
    description: "",
    photoUrl: "",
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent, journeyPrompt?: string) => {
    e.preventDefault();
    const messageContent = journeyPrompt || input.trim();
    if (!messageContent || loading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: messageContent }]);
    setLoading(true);

    // Show reasoning modal
    const mockData: MockMemoryData = journeyPrompt?.includes("home") 
      ? ourHomeMockData 
      : ourHomeMockData; // You can add more mock data sets here

    setReasoningModal({
      visible: true,
      reasoning: mockData.reasoning,
      paraphrasedQuery: mockData.paraphrasedQuery
    });

    // Simulate reasoning time
    setTimeout(() => {
      setReasoningModal(null);
      setLoading(false);
      
      // Start auto-playing memories
      setAutoPlayingMemories({
        memories: mockData.memories,
        currentIndex: 0,
        isPlaying: true
      });

      // Add message with memories
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I found some beautiful memories about your home. Let me show you...",
          memories: mockData.memories,
          currentMemoryIndex: 0
        },
      ]);
    }, 3000);
  };

  // Auto-play effect
  useEffect(() => {
    if (autoPlayingMemories && autoPlayingMemories.isPlaying) {
      const duration = autoPlayingMemories.memories[autoPlayingMemories.currentIndex].type === "video" 
        ? 8000  // 8 seconds for videos
        : 5000; // 5 seconds for photos

      autoPlayTimerRef.current = setTimeout(() => {
        if (autoPlayingMemories.currentIndex < autoPlayingMemories.memories.length - 1) {
          setAutoPlayingMemories({
            ...autoPlayingMemories,
            currentIndex: autoPlayingMemories.currentIndex + 1
          });
        } else {
          // Finished showing all memories
          setAutoPlayingMemories(null);
        }
      }, duration);
    }

    return () => {
      if (autoPlayTimerRef.current) {
        clearTimeout(autoPlayTimerRef.current);
      }
    };
  }, [autoPlayingMemories]);

  const stopAutoPlay = () => {
    if (autoPlayTimerRef.current) {
      clearTimeout(autoPlayTimerRef.current);
    }
    setAutoPlayingMemories(null);
  };

  const openMemoryViewer = (memories: MemoryItem[], messageIndex: number) => {
    setViewingMemoryModal({
      memories,
      currentIndex: 0,
      messageIndex
    });
  };

  const nextMemory = () => {
    if (viewingMemoryModal && viewingMemoryModal.currentIndex < viewingMemoryModal.memories.length - 1) {
      setViewingMemoryModal({
        ...viewingMemoryModal,
        currentIndex: viewingMemoryModal.currentIndex + 1
      });
    }
  };

  const previousMemory = () => {
    if (viewingMemoryModal && viewingMemoryModal.currentIndex > 0) {
      setViewingMemoryModal({
        ...viewingMemoryModal,
        currentIndex: viewingMemoryModal.currentIndex - 1
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-memory flex flex-col">
      {/* Header */}
      <header className="border-b border-purple/20 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <Link to="/" className="flex items-center gap-2">
            <BrainLogo size="sm" />
            <span className="text-white font-medium">Memory Retriever x LORAN</span>
          </Link>
          <button
            onClick={() => setShowProfileModal(true)}
            className="p-2 hover:bg-purple/10 rounded-lg transition-colors"
          >
            <UserCircle className="w-6 h-6 text-purple" />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex flex-col max-w-7xl w-full mx-auto gap-8 px-6 py-8">
        {/* Journey Selection or Chat */}
        <div className="flex-1 flex flex-col">
          {messages.length <= 1 && (
            <div className="flex-1 flex flex-col items-center justify-center gap-12">
              {/* Memory Journeys Section */}
              <div className="w-full">
                <h2 className="text-2xl font-light text-white text-center mb-3 animate-fade-in">
                  ✨ Memory Journeys
                </h2>
                <p className="text-gray-400 text-center text-sm mb-8 animate-fade-in animate-delay-100">
                  Choose a path to begin a conversation
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {journeys.map((journey, idx) => (
                    <button
                      key={journey.id}
                      onClick={(e) => handleSendMessage(e, `Tell me about ${journey.title.toLowerCase()}`)}
                      className={`group relative p-4 rounded-lg border border-purple/30 bg-gradient-to-br ${journey.color} hover:border-purple/60 hover:shadow-lg hover:shadow-purple/20 transition-all duration-300 text-left transform hover:scale-105 animate-scale-in`}
                      style={{ animationDelay: `${idx * 0.1}s`, animationFillMode: 'both' }}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <span className="text-2xl group-hover:scale-110 transition-transform">{journey.icon}</span>
                        <svg className="w-4 h-4 text-purple opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                      <h3 className="text-white font-medium text-lg">{journey.title}</h3>
                      <p className="text-gray-400 text-sm mt-1">{journey.subtitle}</p>
                    </button>
                  ))}
                </div>

                <p className="text-gray-500 text-center text-xs mt-8 animate-fade-in animate-delay-400">
                  Or simply start typing to explore your memories...
                </p>
              </div>
            </div>
          )}

          {messages.length > 1 && (
            <div className="flex-1 overflow-y-auto space-y-4 mb-6">
              {messages.map((message, idx) => (
                <div key={idx}>
                  <div
                    className={`flex ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-md lg:max-w-xl px-4 py-3 rounded-lg ${
                        message.role === "user"
                          ? "bg-purple/20 text-white border border-purple/30"
                          : "bg-purple/10 text-gray-100 border border-purple/20"
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                    </div>
                  </div>
                  
                  {/* Memory Preview Thumbnails */}
                  {message.memories && message.memories.length > 0 && (
                    <div className="flex justify-start mt-3 animate-fade-in">
                      <div className="max-w-md lg:max-w-xl">
                        <div className="flex gap-2 flex-wrap">
                          {message.memories.map((memory, memIdx) => (
                            <button
                              key={memory.id}
                              onClick={() => openMemoryViewer(message.memories!, idx)}
                              className="relative w-24 h-24 rounded-lg overflow-hidden border-2 border-purple/30 hover:border-purple hover:shadow-lg hover:shadow-purple/30 transition-all group transform hover:scale-110 animate-scale-in"
                              style={{ animationDelay: `${memIdx * 0.05}s`, animationFillMode: 'both' }}
                            >
                              <img
                                src={memory.mediaUrl}
                                alt={memory.title}
                                className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                              />
                              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-2">
                                <span className="text-white text-xs font-medium line-clamp-2">
                                  {memory.title}
                                </span>
                              </div>
                              {memory.type === "video" && (
                                <div className="absolute inset-0 flex items-center justify-center">
                                  <div className="w-8 h-8 bg-black/50 rounded-full flex items-center justify-center">
                                    <svg className="w-4 h-4 text-white ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                                      <path d="M8 5v14l11-7z" />
                                    </svg>
                                  </div>
                                </div>
                              )}
                            </button>
                          ))}
                        </div>
                        <p className="text-xs text-gray-400 mt-2">
                          Click to view memories ({message.memories.length} found)
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-purple/10 text-gray-100 border border-purple/20 px-4 py-3 rounded-lg">
                    <div className="flex gap-2">
                      <div className="w-2 h-2 bg-purple rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-purple rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                      <div className="w-2 h-2 bg-purple rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      {/* Chat Input */}
      <div className="border-t border-purple/20 px-6 py-6 bg-gradient-memory/50 backdrop-blur-sm">
        <form
          onSubmit={handleSendMessage}
          className="max-w-7xl mx-auto flex gap-3"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about your memories..."
            className="flex-1 bg-purple/10 border border-purple/30 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple/60 transition-colors"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="bg-purple hover:bg-purple/80 text-white p-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>

      {/* Reasoning Modal */}
      {reasoningModal && reasoningModal.visible && (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="max-w-2xl mx-auto px-8 text-center space-y-8">
            {/* AI Brain Animation */}
            <div className="flex justify-center">
              <div className="relative">
                <BrainLogo size="lg" className="animate-pulse" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-32 h-32 border-4 border-purple/30 border-t-purple rounded-full animate-spin"></div>
                </div>
              </div>
            </div>

            {/* Reasoning Text */}
            <div className="space-y-4">
              <h3 className="text-cyan text-lg font-medium">Reasoning...</h3>
              <p className="text-gray-300 text-sm leading-relaxed italic">
                "{reasoningModal.paraphrasedQuery}"
              </p>
              <div className="flex items-center justify-center gap-2 text-purple">
                <div className="w-2 h-2 bg-purple rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-purple rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                <div className="w-2 h-2 bg-purple rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
              </div>
              <p className="text-gray-400 text-xs">
                {reasoningModal.reasoning}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Auto-Playing Memory Viewer */}
      {autoPlayingMemories && (
        <div className="fixed inset-0 bg-black z-50 flex items-center justify-center">
          {/* Skip/Stop button */}
          <button
            onClick={stopAutoPlay}
            className="absolute top-6 right-6 px-4 py-2 bg-purple/80 hover:bg-purple rounded-lg transition-colors z-10 flex items-center gap-2"
          >
            <X className="w-4 h-4 text-white" />
            <span className="text-white text-sm">Skip Auto-Play</span>
          </button>

          {/* Progress indicator */}
          <div className="absolute top-6 left-6 z-10">
            <div className="bg-black/50 rounded-lg px-4 py-2 backdrop-blur-sm">
              <p className="text-white text-sm">
                Memory {autoPlayingMemories.currentIndex + 1} of {autoPlayingMemories.memories.length}
              </p>
            </div>
          </div>

          {/* Memory Content */}
          <div className="w-full h-full flex items-center justify-center p-8">
            <div className="relative max-w-7xl w-full">
              {/* Memory Title - Outside of media */}
              <div className="mb-6 px-4">
                <h2 className="text-white text-2xl md:text-3xl font-light tracking-wider animate-fade-in">
                  {autoPlayingMemories.memories[autoPlayingMemories.currentIndex].title}
                </h2>
              </div>

              {/* Memory Media and Description Container */}
              <div className="relative flex items-center gap-6">
                {/* Memory Media */}
                <div className="flex-shrink-0 rounded-lg overflow-hidden shadow-2xl" style={{ maxWidth: '60%' }}>
                  {autoPlayingMemories.memories[autoPlayingMemories.currentIndex].type === "photo" ? (
                    <img
                      src={autoPlayingMemories.memories[autoPlayingMemories.currentIndex].mediaUrl}
                      alt={autoPlayingMemories.memories[autoPlayingMemories.currentIndex].title}
                      className="w-full h-auto max-h-[70vh] object-cover animate-fade-in rounded-lg"
                    />
                  ) : (
                    <video
                      key={autoPlayingMemories.memories[autoPlayingMemories.currentIndex].id}
                      src={autoPlayingMemories.memories[autoPlayingMemories.currentIndex].mediaUrl}
                      autoPlay
                      muted
                      className="w-full h-auto max-h-[70vh] rounded-lg"
                    />
                  )}
                </div>

                {/* Description Box - Right Side with Blur */}
                <div className="flex-1 backdrop-blur-xl bg-black/40 rounded-lg p-6 border border-white/10 shadow-2xl animate-fade-in">
                  <p className="text-white text-base md:text-lg leading-relaxed">
                    {autoPlayingMemories.memories[autoPlayingMemories.currentIndex].description}
                  </p>
                  {autoPlayingMemories.memories[autoPlayingMemories.currentIndex].timestamp && (
                    <p className="text-gray-300 text-sm mt-4 pt-4 border-t border-white/10">
                      {autoPlayingMemories.memories[autoPlayingMemories.currentIndex].timestamp}
                    </p>
                  )}
                </div>
              </div>

              {/* Progress Bar */}
              <div className="flex gap-1 mt-6 px-4">
                {autoPlayingMemories.memories.map((_, idx) => (
                  <div
                    key={idx}
                    className={`flex-1 h-1 rounded-full transition-all ${
                      idx < autoPlayingMemories.currentIndex
                        ? "bg-purple"
                        : idx === autoPlayingMemories.currentIndex
                        ? "bg-purple animate-pulse"
                        : "bg-gray-600"
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Memory Viewer Modal - Full Screen */}
      {viewingMemoryModal && (
        <div className="fixed inset-0 bg-black z-50 flex items-center justify-center">
          <button
            onClick={() => setViewingMemoryModal(null)}
            className="absolute top-6 right-6 p-2 hover:bg-white/10 rounded-full transition-colors z-10"
          >
            <X className="w-6 h-6 text-white" />
          </button>

          {/* Navigation Arrows */}
          {viewingMemoryModal.currentIndex > 0 && (
            <button
              onClick={previousMemory}
              className="absolute left-6 p-3 bg-black/50 hover:bg-black/70 rounded-full transition-colors z-10"
            >
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
          )}
          
          {viewingMemoryModal.currentIndex < viewingMemoryModal.memories.length - 1 && (
            <button
              onClick={nextMemory}
              className="absolute right-6 p-3 bg-black/50 hover:bg-black/70 rounded-full transition-colors z-10"
            >
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          )}

          {/* Memory Content */}
          <div className="w-full h-full flex items-center justify-center p-8">
            <div className="relative max-w-7xl w-full">
              {/* Memory Title - Outside of media */}
              <div className="mb-6 px-4">
                <h2 className="text-white text-2xl md:text-3xl font-light tracking-wider">
                  {viewingMemoryModal.memories[viewingMemoryModal.currentIndex].title}
                </h2>
              </div>

              {/* Memory Media and Description Container */}
              <div className="relative flex items-center gap-6">
                {/* Memory Media */}
                <div className="flex-shrink-0 rounded-lg overflow-hidden shadow-2xl" style={{ maxWidth: '60%' }}>
                  {viewingMemoryModal.memories[viewingMemoryModal.currentIndex].type === "photo" ? (
                    <img
                      src={viewingMemoryModal.memories[viewingMemoryModal.currentIndex].mediaUrl}
                      alt={viewingMemoryModal.memories[viewingMemoryModal.currentIndex].title}
                      className="w-full h-auto max-h-[70vh] object-cover rounded-lg"
                    />
                  ) : (
                    <video
                      src={viewingMemoryModal.memories[viewingMemoryModal.currentIndex].mediaUrl}
                      controls
                      className="w-full h-auto max-h-[70vh] rounded-lg"
                    />
                  )}
                </div>

                {/* Description Box - Right Side with Blur */}
                <div className="flex-1 backdrop-blur-xl bg-black/40 rounded-lg p-6 border border-white/10 shadow-2xl">
                  <p className="text-white text-base md:text-lg leading-relaxed">
                    {viewingMemoryModal.memories[viewingMemoryModal.currentIndex].description}
                  </p>
                  {viewingMemoryModal.memories[viewingMemoryModal.currentIndex].timestamp && (
                    <p className="text-gray-300 text-sm mt-4 pt-4 border-t border-white/10">
                      {viewingMemoryModal.memories[viewingMemoryModal.currentIndex].timestamp}
                    </p>
                  )}
                </div>
              </div>

              {/* Progress Indicator */}
              <div className="flex justify-center gap-2 mt-6 px-4">
                {viewingMemoryModal.memories.map((_, idx) => (
                  <button
                    key={idx}
                    onClick={() => setViewingMemoryModal({ ...viewingMemoryModal, currentIndex: idx })}
                    className={`h-1.5 rounded-full transition-all ${
                      idx === viewingMemoryModal.currentIndex
                        ? "w-8 bg-purple"
                        : "w-1.5 bg-gray-500 hover:bg-gray-400"
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Patient Profile Modal */}
      {showProfileModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 px-4">
          <div className="bg-gradient-to-br from-purple/20 to-purple/10 border border-purple/30 rounded-lg p-6 w-full max-w-md shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full border border-purple bg-purple/20 flex items-center justify-center">
                  <UserCircle className="w-4 h-4 text-purple" />
                </div>
                <h2 className="text-lg font-medium text-white">Patient Profile</h2>
              </div>
              <button
                onClick={() => setShowProfileModal(false)}
                className="p-1 hover:bg-purple/20 rounded transition-colors"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>

            {/* Profile Photo Section */}
            <div className="mb-6">
              <label className="text-sm text-magenta font-medium flex items-center gap-1 mb-4">
                <UserCircle className="w-4 h-4" />
                Profile Photo
              </label>
              <div className="flex flex-col items-center gap-4">
                <div className="w-20 h-20 rounded-full border-2 border-purple/40 bg-purple/10 flex items-center justify-center">
                  {profileData.photoUrl ? (
                    <img
                      src={profileData.photoUrl}
                      alt="Profile"
                      className="w-full h-full rounded-full object-cover"
                    />
                  ) : (
                    <UserCircle className="w-10 h-10 text-purple/60" />
                  )}
                </div>
                <label className="cursor-pointer flex items-center gap-2 text-sm text-white hover:text-gray-300 transition-colors">
                  <Upload className="w-4 h-4" />
                  Upload Photo
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        const reader = new FileReader();
                        reader.onloadend = () => {
                          setProfileData((prev) => ({
                            ...prev,
                            photoUrl: reader.result as string,
                          }));
                        };
                        reader.readAsDataURL(file);
                      }
                    }}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* Patient Name */}
            <div className="mb-6">
              <label className="block text-sm text-gray-300 font-medium mb-2">
                Patient name
              </label>
              <input
                type="text"
                value={profileData.name}
                onChange={(e) =>
                  setProfileData((prev) => ({ ...prev, name: e.target.value }))
                }
                placeholder="Mary Jane"
                className="w-full bg-purple/20 border border-purple/30 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-purple/60 transition-colors"
              />
            </div>

            {/* Description */}
            <div className="mb-6">
              <label className="block text-sm text-magenta font-medium mb-2">
                Description
              </label>
              <textarea
                value={profileData.description}
                onChange={(e) =>
                  setProfileData((prev) => ({
                    ...prev,
                    description: e.target.value,
                  }))
                }
                placeholder="Loving mother, grandmother, and the heart of our family."
                rows={4}
                className="w-full bg-purple/20 border border-purple/30 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-purple/60 transition-colors resize-none"
              />
            </div>

            {/* Buttons */}
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowProfileModal(false)}
                className="px-4 py-2 text-gray-300 border border-purple/30 rounded-lg hover:bg-purple/10 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  console.log("Profile saved:", profileData);
                  setShowProfileModal(false);
                }}
                className="px-4 py-2 bg-purple hover:bg-purple/80 text-white rounded-lg transition-colors flex items-center gap-2"
              >
                <svg
                  className="w-4 h-4"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                </svg>
                Save Profile
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
