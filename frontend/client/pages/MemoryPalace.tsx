import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import { Send, UserCircle, X, Upload } from "lucide-react";

interface JourneyCard {
  id: string;
  title: string;
  subtitle: string;
  icon: string;
  color: string;
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
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([
    {
      role: "assistant",
      content: "Welcome to your Memory Palace. What would you like to explore today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
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

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    // Simulate API call - replace with actual Gemini API integration
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "That's a wonderful memory. Let me weave together some stories for you from your collection.",
        },
      ]);
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gradient-memory flex flex-col">
      {/* Header */}
      <header className="border-b border-purple/20 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full border-2 border-purple bg-purple/10 flex items-center justify-center">
              <svg
                className="w-5 h-5 text-purple"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
              </svg>
            </div>
            <span className="text-white font-medium">Memory Palace</span>
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
                <h2 className="text-2xl font-light text-white text-center mb-3">
                  ✨ Memory Journeys
                </h2>
                <p className="text-gray-400 text-center text-sm mb-8">
                  Choose a path to begin a conversation
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  {journeys.map((journey) => (
                    <button
                      key={journey.id}
                      onClick={() => handleSendMessage({
                        preventDefault: () => {},
                      } as any)}
                      className={`group relative p-4 rounded-lg border border-purple/30 bg-gradient-to-br ${journey.color} hover:border-purple/60 transition-all duration-300 text-left`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <span className="text-2xl">{journey.icon}</span>
                        <svg className="w-4 h-4 text-purple opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                      <h3 className="text-white font-medium text-lg">{journey.title}</h3>
                      <p className="text-gray-400 text-sm mt-1">{journey.subtitle}</p>
                    </button>
                  ))}
                </div>

                <p className="text-gray-500 text-center text-xs mt-8">
                  Or simply start typing to explore your memories...
                </p>
              </div>
            </div>
          )}

          {messages.length > 1 && (
            <div className="flex-1 overflow-y-auto space-y-4 mb-6">
              {messages.map((message, idx) => (
                <div
                  key={idx}
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
