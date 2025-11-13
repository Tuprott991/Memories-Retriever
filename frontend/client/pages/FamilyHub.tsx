import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import { Upload, Music, FileText, Image, Video, Mic, Square, X, Trash2, Edit2 } from "lucide-react";
import * as faceapi from "@vladmandic/face-api";

interface DetectedFace {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
  name: string;
  description: string;
}

// Memory metadata only (NO images/audio - those stay in session)
interface MemoryMetadata {
  id: string;
  type: "photo" | "video" | "voice" | "note";
  title: string;
  description: string;
  timestamp: string;
  faces?: DetectedFace[];
  noteContent?: string;
}

// Session-only file data
interface UploadSession {
  file: File;
  preview: string;
  videoThumbnail?: string;
  audioDuration?: number;
}

export default function FamilyHub() {
  // Metadata stored in localStorage
  const [memoryMetadata, setMemoryMetadata] = useState<MemoryMetadata[]>([]);
  // Session-only file data
  const [uploadedFiles, setUploadedFiles] = useState<Map<string, UploadSession>>(new Map());
  
  const [activeTab, setActiveTab] = useState<"photos" | "videos" | "voice" | "notes">("photos");
  const [uploadingFiles, setUploadingFiles] = useState<File[]>([]);
  const [currentUploadIndex, setCurrentUploadIndex] = useState(0);
  const [uploadFormData, setUploadFormData] = useState({ title: "", description: "" });
  const [detectedFaces, setDetectedFaces] = useState<DetectedFace[]>([]);
  const [selectedFaceId, setSelectedFaceId] = useState<string | null>(null);
  const [faceAnnotation, setFaceAnnotation] = useState({ name: "", description: "" });
  const [isRecording, setIsRecording] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editFormData, setEditFormData] = useState({ title: "", description: "" });
  const [currentPreview, setCurrentPreview] = useState("");
  const [hoveredFaceId, setHoveredFaceId] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const previewCanvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  // Load metadata from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("memoryMetadata");
    if (saved) {
      setMemoryMetadata(JSON.parse(saved));
    }
    loadFaceDetectionModel();
  }, []);

  // Save metadata to localStorage when it changes
  useEffect(() => {
    localStorage.setItem("memoryMetadata", JSON.stringify(memoryMetadata));
  }, [memoryMetadata]);

  const loadFaceDetectionModel = async () => {
    try {
      const modelUrl = "https://cdn.jsdelivr.net/npm/@vladmandic/face-api@1.7.15/model/";
      await faceapi.nets.tinyFaceDetector.load(modelUrl);
    } catch (error) {
      console.error("Error loading face detection model:", error);
    }
  };

  const detectFacesInImage = async (imageUrl: string) => {
    try {
      const img = new Image();
      img.src = imageUrl;
      img.onload = async () => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext("2d");
        if (ctx) ctx.drawImage(img, 0, 0);

        const detections = await faceapi.detectAllTinyFaces(canvas, {
          scoreThreshold: 0.5,
        });

        const faces: DetectedFace[] = detections.map((det, idx) => ({
          id: `face-${idx}`,
          x: det.box.x,
          y: det.box.y,
          width: det.box.width,
          height: det.box.height,
          name: "",
          description: "",
        }));

        setDetectedFaces(faces);
      };
    } catch (error) {
      console.error("Error detecting faces:", error);
    }
  };

  const drawFaceBoxes = (imageUrl: string, faces: DetectedFace[]) => {
    const img = new Image();
    img.src = imageUrl;
    img.onload = () => {
      const canvas = previewCanvasRef.current;
      if (!canvas) return;

      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      ctx.drawImage(img, 0, 0);
      ctx.strokeStyle = "#b366ff";
      ctx.lineWidth = 2;
      ctx.font = "14px Arial";
      ctx.fillStyle = "#b366ff";

      faces.forEach((face) => {
        ctx.strokeRect(face.x, face.y, face.width, face.height);
        if (face.name) {
          ctx.fillText(face.name, face.x, face.y - 5);
        }
      });
    };
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      setUploadingFiles(Array.from(files));
      setCurrentUploadIndex(0);
      setUploadFormData({ title: "", description: "" });
      setDetectedFaces([]);
      processFirstFile(files[0]);
    }
  };

  const processFirstFile = async (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const preview = e.target?.result as string;
      setCurrentPreview(preview);

      if (activeTab === "photos") {
        detectFacesInImage(preview);
      } else if (activeTab === "videos") {
        generateVideoThumbnail(file, preview);
      }
    };
    reader.readAsDataURL(file);
  };

  const generateVideoThumbnail = (file: File, preview: string) => {
    const video = document.createElement("video");
    const reader = new FileReader();

    reader.onload = (e) => {
      const blob = new Blob([e.target?.result as ArrayBuffer], { type: file.type });
      const url = URL.createObjectURL(blob);
      video.src = url;

      video.onloadedmetadata = () => {
        video.currentTime = 0;
      };

      video.onseeked = () => {
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext("2d");
        ctx?.drawImage(video, 0, 0);
        setCurrentPreview(canvas.toDataURL());
        URL.revokeObjectURL(url);
      };
    };

    reader.readAsArrayBuffer(file);
  };

  const saveCurrentUpload = () => {
    if (!uploadFormData.title.trim()) return;

    const file = uploadingFiles[currentUploadIndex];
    const newMetadata: MemoryMetadata = {
      id: Date.now().toString(),
      type: activeTab.slice(0, -1) as any,
      title: uploadFormData.title,
      description: uploadFormData.description,
      timestamp: new Date().toLocaleDateString(),
      faces: activeTab === "photos" ? detectedFaces : undefined,
      noteContent: activeTab === "notes" ? uploadFormData.description : undefined,
    };

    // Store metadata in localStorage
    setMemoryMetadata((prev) => [newMetadata, ...prev]);

    // Store file preview in session memory
    setUploadedFiles((prev) => {
      const map = new Map(prev);
      map.set(newMetadata.id, {
        file,
        preview: currentPreview,
      });
      return map;
    });

    // Move to next file or finish
    if (currentUploadIndex + 1 < uploadingFiles.length) {
      setCurrentUploadIndex(currentUploadIndex + 1);
      setUploadFormData({ title: "", description: "" });
      setDetectedFaces([]);
      setSelectedFaceId(null);
      processFirstFile(uploadingFiles[currentUploadIndex + 1]);
    } else {
      setUploadingFiles([]);
      setCurrentUploadIndex(0);
      setUploadFormData({ title: "", description: "" });
      setDetectedFaces([]);
      setCurrentPreview("");
    }
  };

  const handleStartRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        const timestamp = new Date().toLocaleTimeString();
        const newMetadata: MemoryMetadata = {
          id: Date.now().toString(),
          type: "voice",
          title: `Voice Note - ${timestamp}`,
          description: "",
          timestamp: new Date().toLocaleDateString(),
        };

        setMemoryMetadata((prev) => [newMetadata, ...prev]);

        // Store audio blob in session
        setUploadedFiles((prev) => {
          const map = new Map(prev);
          map.set(newMetadata.id, {
            file: new File([audioBlob], `voice-${timestamp}.webm`, { type: "audio/webm" }),
            preview: "",
          });
          return map;
        });

        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  };

  const handleStopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const deleteMemory = (id: string) => {
    setMemoryMetadata((prev) => prev.filter((m) => m.id !== id));
    setUploadedFiles((prev) => {
      const map = new Map(prev);
      map.delete(id);
      return map;
    });
  };

  const startEdit = (memory: MemoryMetadata) => {
    setEditingId(memory.id);
    setEditFormData({ title: memory.title, description: memory.description });
  };

  const saveEdit = (id: string) => {
    setMemoryMetadata((prev) =>
      prev.map((m) =>
        m.id === id ? { ...m, title: editFormData.title, description: editFormData.description } : m
      )
    );
    setEditingId(null);
  };

  const stats = {
    photos: memoryMetadata.filter((m) => m.type === "photo").length,
    videos: memoryMetadata.filter((m) => m.type === "video").length,
    voice: memoryMetadata.filter((m) => m.type === "voice").length,
    notes: memoryMetadata.filter((m) => m.type === "note").length,
  };

  useEffect(() => {
    if (activeTab === "photos" && currentPreview && detectedFaces.length > 0) {
      drawFaceBoxes(currentPreview, detectedFaces);
    }
  }, [detectedFaces, hoveredFaceId]);

  return (
    <div className="min-h-screen bg-gradient-memory flex flex-col">
      {/* Header */}
      <header className="border-b border-purple/20 px-6 py-6">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full border-2 border-purple bg-purple/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-purple" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
              </svg>
            </div>
            <span className="text-white font-medium text-lg">Memory Palace</span>
          </Link>
          <h1 className="text-2xl font-light text-white">Family Hub</h1>
          <div className="w-10"></div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex flex-col max-w-7xl w-full mx-auto px-6 py-8 gap-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { icon: Image, label: "Photos", count: stats.photos, color: "cyan" },
            { icon: Video, label: "Videos", count: stats.videos, color: "teal" },
            { icon: Music, label: "Voice", count: stats.voice, color: "purple" },
            { icon: FileText, label: "Notes", count: stats.notes, color: "magenta" },
          ].map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className="p-4 rounded-lg border border-purple/30 bg-purple/5 backdrop-blur-sm">
                <div className="flex items-center gap-3 mb-2">
                  <Icon className={`w-5 h-5 text-${stat.color}`} />
                  <span className="text-gray-400 text-sm">{stat.label}</span>
                </div>
                <p className="text-3xl font-light text-white">{stat.count}</p>
              </div>
            );
          })}
        </div>

        {/* Tabs */}
        <div className="flex border-b border-purple/20 gap-1">
          {(["photos", "videos", "voice", "notes"] as const).map((tab) => {
            const icons = {
              photos: Image,
              videos: Video,
              voice: Music,
              notes: FileText,
            };
            const Icon = icons[tab];
            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                  activeTab === tab
                    ? "border-purple text-white"
                    : "border-transparent text-gray-400 hover:text-gray-300"
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            );
          })}
        </div>

        {/* Upload Section or File Preview */}
        {uploadingFiles.length === 0 ? (
          <div className="bg-purple/10 border border-purple/30 rounded-lg p-6">
            <h2 className="text-xl font-light text-white mb-6">Upload Memories</h2>

            {activeTab === "voice" && (
              <div className="space-y-4">
                <div className="border-2 border-dashed border-purple/30 rounded-lg p-8 text-center">
                  {!isRecording ? (
                    <button
                      onClick={handleStartRecording}
                      className="w-full flex flex-col items-center gap-3 hover:opacity-80 transition-opacity"
                    >
                      <Mic className="w-12 h-12 text-purple/60" />
                      <p className="text-white font-medium">Record Voice Note</p>
                      <p className="text-gray-400 text-sm">Click to start recording</p>
                    </button>
                  ) : (
                    <button
                      onClick={handleStopRecording}
                      className="w-full flex flex-col items-center gap-3 animate-pulse"
                    >
                      <div className="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center">
                        <Square className="w-6 h-6 text-red-500" />
                      </div>
                      <p className="text-white font-medium">Stop Recording</p>
                      <p className="text-red-400 text-sm">Recording in progress...</p>
                    </button>
                  )}
                </div>

                <div className="flex items-center gap-3">
                  <div className="flex-1 border-t border-purple/20"></div>
                  <span className="text-gray-400 text-sm">OR</span>
                  <div className="flex-1 border-t border-purple/20"></div>
                </div>

                <div
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-purple/30 rounded-lg p-8 text-center hover:border-purple/60 transition-colors cursor-pointer"
                >
                  <Upload className="w-12 h-12 text-purple/60 mx-auto mb-3" />
                  <p className="text-white font-medium mb-1">Click to upload audio</p>
                  <p className="text-gray-400 text-sm">or drag and drop your audio files</p>
                </div>
              </div>
            )}

            {(activeTab === "photos" || activeTab === "videos") && (
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-purple/30 rounded-lg p-8 text-center hover:border-purple/60 transition-colors cursor-pointer"
              >
                <Upload className="w-12 h-12 text-purple/60 mx-auto mb-3" />
                <p className="text-white font-medium mb-1">Click to upload</p>
                <p className="text-gray-400 text-sm">or drag and drop your files</p>
              </div>
            )}

            {activeTab === "notes" && (
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Note title"
                  value={uploadFormData.title}
                  onChange={(e) => setUploadFormData((prev) => ({ ...prev, title: e.target.value }))}
                  className="w-full bg-purple/20 border border-purple/30 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-purple/60"
                />
                <textarea
                  placeholder="Note content"
                  value={uploadFormData.description}
                  onChange={(e) => setUploadFormData((prev) => ({ ...prev, description: e.target.value }))}
                  rows={6}
                  className="w-full bg-purple/20 border border-purple/30 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-purple/60 resize-none"
                />
                <button
                  onClick={() => {
                    if (uploadFormData.title.trim()) {
                      const newMetadata: MemoryMetadata = {
                        id: Date.now().toString(),
                        type: "note",
                        title: uploadFormData.title,
                        description: "",
                        timestamp: new Date().toLocaleDateString(),
                        noteContent: uploadFormData.description,
                      };
                      setMemoryMetadata((prev) => [newMetadata, ...prev]);
                      setUploadFormData({ title: "", description: "" });
                    }
                  }}
                  className="w-full bg-purple hover:bg-purple/80 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Save Note
                </button>
              </div>
            )}

            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              multiple={activeTab !== "voice"}
              accept={
                activeTab === "photos" ? "image/*" : activeTab === "videos" ? "video/*" : "audio/*"
              }
              onChange={handleFileSelect}
            />
          </div>
        ) : (
          <div className="bg-purple/10 border border-purple/30 rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-light text-white">
                {activeTab === "photos" && "Edit Photo"}
                {activeTab === "videos" && "Edit Video"}
                {activeTab === "voice" && "Edit Voice Note"}
              </h2>
              <button
                onClick={() => {
                  setUploadingFiles([]);
                  setCurrentUploadIndex(0);
                  setCurrentPreview("");
                }}
                className="p-1 hover:bg-purple/20 rounded transition-colors"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>

            {/* Image Preview with Face Detection Overlay */}
            {(activeTab === "photos" || activeTab === "videos") && currentPreview && (
              <div className="flex justify-center mb-6 relative">
                {activeTab === "photos" && detectedFaces.length > 0 ? (
                  <canvas
                    ref={previewCanvasRef}
                    className="max-w-full h-auto rounded-lg max-h-96 cursor-pointer"
                    onClick={(e) => {
                      const rect = (e.target as HTMLCanvasElement).getBoundingClientRect();
                      const x = e.clientX - rect.left;
                      const y = e.clientY - rect.top;

                      detectedFaces.forEach((face) => {
                        if (
                          x >= face.x &&
                          x <= face.x + face.width &&
                          y >= face.y &&
                          y <= face.y + face.height
                        ) {
                          setSelectedFaceId(face.id);
                        }
                      });
                    }}
                  />
                ) : (
                  <img
                    src={currentPreview}
                    alt="Preview"
                    className="max-w-full h-auto rounded-lg max-h-96"
                  />
                )}
              </div>
            )}

            {/* Face Detection Annotations (Photos only) */}
            {activeTab === "photos" && detectedFaces.length > 0 && (
              <div className="mt-6 space-y-4">
                <h3 className="text-white font-medium">Detected Faces ({detectedFaces.length})</h3>
                <p className="text-gray-400 text-sm">Click on a face in the image or below to annotate</p>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {detectedFaces.map((face) => (
                    <div
                      key={face.id}
                      onMouseEnter={() => setHoveredFaceId(face.id)}
                      onMouseLeave={() => setHoveredFaceId(null)}
                      onClick={() => setSelectedFaceId(face.id)}
                      className={`p-3 rounded-lg border-2 cursor-pointer transition-colors ${
                        selectedFaceId === face.id
                          ? "border-purple bg-purple/30"
                          : hoveredFaceId === face.id
                            ? "border-purple/60 bg-purple/20"
                            : "border-purple/30 bg-purple/10"
                      }`}
                    >
                      {selectedFaceId === face.id ? (
                        <div className="space-y-2">
                          <input
                            type="text"
                            placeholder="Person name"
                            value={faceAnnotation.name}
                            onChange={(e) => setFaceAnnotation((prev) => ({ ...prev, name: e.target.value }))}
                            className="w-full bg-purple/20 border border-purple/30 rounded px-2 py-1 text-white text-sm placeholder-gray-500 focus:outline-none"
                          />
                          <textarea
                            placeholder="Description"
                            value={faceAnnotation.description}
                            onChange={(e) => setFaceAnnotation((prev) => ({ ...prev, description: e.target.value }))}
                            rows={2}
                            className="w-full bg-purple/20 border border-purple/30 rounded px-2 py-1 text-white text-sm placeholder-gray-500 focus:outline-none resize-none"
                          />
                          <div className="flex gap-2 text-xs">
                            <button
                              onClick={() => {
                                setDetectedFaces((prev) =>
                                  prev.map((f) =>
                                    f.id === face.id
                                      ? { ...f, name: faceAnnotation.name, description: faceAnnotation.description }
                                      : f
                                  )
                                );
                                setSelectedFaceId(null);
                                setFaceAnnotation({ name: "", description: "" });
                              }}
                              className="flex-1 bg-purple hover:bg-purple/80 text-white px-2 py-1 rounded transition-colors"
                            >
                              Save
                            </button>
                            <button
                              onClick={() => {
                                setSelectedFaceId(null);
                                setFaceAnnotation({ name: "", description: "" });
                              }}
                              className="flex-1 border border-purple/30 text-gray-300 px-2 py-1 rounded hover:bg-purple/10"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div>
                          <p className="text-white font-medium text-sm">{face.name || "Unknown"}</p>
                          {face.description && (
                            <p className="text-gray-400 text-xs">{face.description}</p>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Title and Description Form */}
            <div className="mt-6 space-y-4">
              <input
                type="text"
                placeholder="Memory title"
                value={uploadFormData.title}
                onChange={(e) => setUploadFormData((prev) => ({ ...prev, title: e.target.value }))}
                className="w-full bg-purple/20 border border-purple/30 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-purple/60"
              />
              <textarea
                placeholder="Memory description"
                value={uploadFormData.description}
                onChange={(e) => setUploadFormData((prev) => ({ ...prev, description: e.target.value }))}
                rows={3}
                className="w-full bg-purple/20 border border-purple/30 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-purple/60 resize-none"
              />
              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => {
                    setUploadingFiles([]);
                    setCurrentUploadIndex(0);
                    setCurrentPreview("");
                  }}
                  className="px-4 py-2 border border-purple/30 text-gray-300 rounded-lg hover:bg-purple/10 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={saveCurrentUpload}
                  className="px-4 py-2 bg-purple hover:bg-purple/80 text-white rounded-lg transition-colors"
                >
                  Save Memory
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Recent Memories */}
        {memoryMetadata.length > 0 && (
          <div className="bg-purple/10 border border-purple/30 rounded-lg p-6">
            <h3 className="text-xl font-light text-white mb-6">Recent Memories</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {memoryMetadata.map((memory) => {
                const fileData = uploadedFiles.get(memory.id);
                return (
                  <div
                    key={memory.id}
                    className="relative group bg-purple/20 rounded-lg border border-purple/20 hover:border-purple/40 overflow-hidden transition-colors"
                  >
                    {/* Thumbnail */}
                    {(memory.type === "photo" || memory.type === "video") && fileData?.preview && (
                      <div className="relative w-full h-40 bg-black">
                        <img
                          src={fileData.preview}
                          alt={memory.title}
                          className="w-full h-full object-cover"
                        />
                        {memory.type === "video" && (
                          <div className="absolute inset-0 flex items-center justify-center bg-black/40">
                            <Video className="w-8 h-8 text-white" />
                          </div>
                        )}
                        {memory.type === "photo" && memory.faces && memory.faces.length > 0 && (
                          <div className="absolute inset-0 flex items-center justify-center bg-black/20">
                            <span className="text-white text-xs bg-black/60 px-2 py-1 rounded">
                              {memory.faces.length} faces
                            </span>
                          </div>
                        )}
                      </div>
                    )}

                    {memory.type === "voice" && (
                      <div className="w-full h-40 bg-gradient-to-br from-purple/20 to-purple/10 flex items-center justify-center">
                        <div className="text-center">
                          <Music className="w-8 h-8 text-purple mx-auto mb-2" />
                          <p className="text-xs text-gray-400">Voice Note</p>
                        </div>
                      </div>
                    )}

                    {memory.type === "note" && (
                      <div className="w-full h-40 bg-gradient-to-br from-purple/20 to-purple/10 p-4 overflow-hidden">
                        <p className="text-white text-sm line-clamp-6">{memory.noteContent}</p>
                      </div>
                    )}

                    {/* Info Section */}
                    <div className="p-4">
                      {editingId === memory.id ? (
                        <div className="space-y-2">
                          <input
                            type="text"
                            value={editFormData.title}
                            onChange={(e) =>
                              setEditFormData((prev) => ({ ...prev, title: e.target.value }))
                            }
                            className="w-full bg-purple/20 border border-purple/30 rounded px-2 py-1 text-white text-sm"
                          />
                          <textarea
                            value={editFormData.description}
                            onChange={(e) =>
                              setEditFormData((prev) => ({ ...prev, description: e.target.value }))
                            }
                            rows={2}
                            className="w-full bg-purple/20 border border-purple/30 rounded px-2 py-1 text-white text-sm resize-none"
                          />
                          <div className="flex gap-2">
                            <button
                              onClick={() => saveEdit(memory.id)}
                              className="flex-1 bg-purple hover:bg-purple/80 text-white px-2 py-1 rounded text-xs transition-colors"
                            >
                              Save
                            </button>
                            <button
                              onClick={() => setEditingId(null)}
                              className="flex-1 border border-purple/30 text-gray-300 px-2 py-1 rounded text-xs hover:bg-purple/10"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <h4 className="text-white font-medium truncate">{memory.title}</h4>
                          <p className="text-gray-400 text-xs mb-2">{memory.timestamp}</p>
                          <p className="text-gray-400 text-sm line-clamp-2">{memory.description}</p>
                        </>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
                      {editingId !== memory.id && (
                        <>
                          <button
                            onClick={() => startEdit(memory)}
                            className="p-2 bg-purple/80 hover:bg-purple text-white rounded transition-colors"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => deleteMemory(memory.id)}
                            className="p-2 bg-red-500/80 hover:bg-red-500 text-white rounded transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Hidden canvases for face detection */}
      <canvas ref={canvasRef} className="hidden" />
      <canvas ref={previewCanvasRef} className="hidden" />
      <img ref={imageRef} className="hidden" />
    </div>
  );
}
