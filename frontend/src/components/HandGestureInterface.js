import React, { useState, useRef, useEffect } from 'react';
import { Camera, Maximize, Minimize, Play, Square, Loader2, Hand, Save, Trash2, Mic, Volume2, Pause, Settings } from 'lucide-react';

const HandGestureInterface = ({
    isLive,
    isProcessing,
    onStartLive,
    onStopLive,
    gestureText,
    onSaveGesture,
    onClearGesture,
    useServerVideo,
    videoRef,
    onOpenLipReading
}) => {
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [isVideoLoaded, setIsVideoLoaded] = useState(false);
    const [videoUrl, setVideoUrl] = useState("http://127.0.0.1:5000/video_feed");

    // TTS State
    const [isPlaying, setIsPlaying] = useState(false);
    const [speechRate, setSpeechRate] = useState(1);
    const [speechVolume, setSpeechVolume] = useState(1);
    const [showSettings, setShowSettings] = useState(false);

    const speakText = () => {
        if (!gestureText) return;
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(gestureText);
        utter.rate = speechRate;
        utter.volume = speechVolume;
        utter.onstart = () => setIsPlaying(true);
        utter.onend = () => setIsPlaying(false);
        window.speechSynthesis.speak(utter);
    };

    const stopSpeech = () => {
        window.speechSynthesis.cancel();
        setIsPlaying(false);
    };

    useEffect(() => {
        setIsVideoLoaded(false);
        if (useServerVideo) {
            setVideoUrl(`http://127.0.0.1:5000/video_feed?t=${Date.now()}`);
        }
    }, [useServerVideo]);

    // Safety: If we receive gesture text, backend is working
    useEffect(() => {
        if (gestureText) setIsVideoLoaded(true);
    }, [gestureText]);

    const handleVideoLoad = () => {
        setIsVideoLoaded(true);
    };

    const toggleFullscreen = () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
            setIsFullscreen(true);
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
                setIsFullscreen(false);
            }
        }
    };

    return (
        <div className="flex flex-col h-full space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

            {/* Header */}
            <div className="flex justify-between items-center px-2">
                <div>
                    <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">Hand Gestures</h2>
                    <p className="text-sm text-bolt-text-secondary">Control and communicate with hand signs</p>
                </div>
                <div className="flex space-x-2">
                    <button
                        onClick={onOpenLipReading}
                        className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-bolt-surface hover:bg-bolt-surface/80 text-gray-400 hover:text-white transition-colors border border-bolt-border hover:border-bolt-primary/50"
                        title="Open Lip Reading"
                    >
                        <Mic size={18} />
                        <span className="text-sm font-medium hidden sm:inline">Lip Reading</span>
                    </button>
                    <button
                        onClick={toggleFullscreen}
                        className="p-2 rounded-lg bg-bolt-surface hover:bg-bolt-surface/80 text-gray-400 hover:text-white transition-colors"
                    >
                        {isFullscreen ? <Minimize size={20} /> : <Maximize size={20} />}
                    </button>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex flex-col lg:flex-row gap-6 flex-grow">

                {/* Video Feed */}
                <div className="flex-1 flex flex-col min-h-[300px] lg:min-h-0 bg-black rounded-2xl overflow-hidden relative shadow-2xl ring-1 ring-bolt-border group">
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
                        {useServerVideo ? (
                            <img
                                src={videoUrl}
                                alt="Gestures Stream"
                                className={`w-full h-full object-cover transform scale-x-[-1] transition-opacity duration-500 ${isVideoLoaded ? 'opacity-100' : 'opacity-0'}`}
                                onLoad={handleVideoLoad}
                                onError={(e) => {
                                    console.log("Video feed error, retrying...", e);
                                    setTimeout(() => setVideoUrl(`http://127.0.0.1:5000/video_feed?t=${Date.now()}`), 1000);
                                }}
                            />
                        ) : (
                            <video
                                ref={videoRef}
                                autoPlay
                                playsInline
                                muted
                                className="w-full h-full object-cover transform scale-x-[-1]"
                            />
                        )}

                        {(isProcessing || (useServerVideo && !isVideoLoaded) || (!isLive && !useServerVideo)) && (
                            <div className="absolute inset-0 flex items-center justify-center bg-black/80 backdrop-blur-sm z-10">
                                {isProcessing || (useServerVideo && !isVideoLoaded) ? (
                                    <div className="text-center text-bolt-accent animate-in fade-in zoom-in duration-300">
                                        <Loader2 size={48} className="mx-auto mb-4 animate-spin" />
                                        <p className="text-lg font-medium">Initializing Vision...</p>
                                        <p className="text-xs text-bolt-text-secondary mt-2">Loading gesture models</p>
                                    </div>
                                ) : (
                                    <div className="text-center text-gray-400">
                                        <Camera size={48} className="mx-auto mb-2 opacity-50" />
                                        <p>Camera inactive</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/90 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-20">
                        <div className="flex justify-center space-x-4">
                            {!isLive ? (
                                <button
                                    onClick={onStartLive}
                                    className="flex items-center space-x-2 px-6 py-3 rounded-full bg-bolt-accent hover:bg-bolt-accent/90 text-white font-bold shadow-lg shadow-bolt-accent/20 transform hover:scale-105 transition-all"
                                >
                                    <Play size={20} fill="currentColor" />
                                    <span>Start Detection</span>
                                </button>
                            ) : (
                                <button
                                    onClick={onStopLive}
                                    className="flex items-center space-x-2 px-6 py-3 rounded-full bg-red-500 hover:bg-red-600 text-white font-bold shadow-lg shadow-red-500/20 transform hover:scale-105 transition-all"
                                >
                                    <Square size={20} fill="currentColor" />
                                    <span>Stop Detection</span>
                                </button>
                            )}
                        </div>
                    </div>

                    {isLive && (
                        <div className="absolute top-4 left-4 flex items-center space-x-2 px-3 py-1 rounded-full bg-bolt-accent/20 backdrop-blur-md border border-bolt-accent/30">
                            <span className="w-2 h-2 rounded-full bg-bolt-accent animate-pulse"></span>
                            <span className="text-xs font-bold text-bolt-accent uppercase tracking-wider">Detecting</span>
                        </div>
                    )}
                </div>

                {/* Gesture Result Section */}
                <div className="flex-1 flex flex-col justify-center items-center p-6 glass-panel rounded-2xl relative overflow-hidden">

                    {/* Background Decorative Icon */}
                    <Hand className="absolute text-bolt-surface opacity-50 transform rotate-12" size={300} strokeWidth={0.5} />

                    <div className="relative z-10 text-center space-y-6 w-full max-w-md">
                        <h3 className="text-gray-400 uppercase tracking-widest font-semibold text-sm">Detected Gesture</h3>

                        <div className="min-h-[120px] flex items-center justify-center">
                            {gestureText ? (
                                <div className="transition-all duration-300 transform scale-100 animate-in zoom-in">
                                    <span className="text-5xl sm:text-7xl font-black bg-clip-text text-transparent bg-gradient-to-b from-white to-gray-400 drop-shadow-2xl">
                                        {gestureText}
                                    </span>
                                </div>
                            ) : (
                                <span className="text-gray-600 italic">No gesture detected</span>
                            )}
                        </div>

                        {gestureText && (
                            <div className="flex justify-center items-center space-x-4 pt-8">
                                <div className="flex items-center space-x-2 bg-bolt-surface/50 rounded-full p-1 border border-bolt-border">
                                    <button
                                        onClick={isPlaying ? stopSpeech : speakText}
                                        disabled={!gestureText}
                                        className="p-2 rounded-full hover:bg-white/10 text-gray-300 disabled:opacity-30 transition-colors tooltip relative"
                                        title="Text to Speech"
                                    >
                                        {isPlaying ? <Pause size={20} /> : <Volume2 size={20} />}
                                    </button>
                                    <div className="relative">
                                        <button
                                            onClick={() => setShowSettings(!showSettings)}
                                            className={`p-2 rounded-full hover:bg-white/10 text-gray-300 transition-colors ${showSettings ? 'bg-white/10 text-white' : ''}`}
                                        >
                                            <Settings size={18} />
                                        </button>
                                        {showSettings && (
                                            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-48 bg-bolt-surface border border-bolt-border rounded-xl p-4 shadow-xl z-30">
                                                <div className="space-y-4">
                                                    <div>
                                                        <label className="text-xs text-gray-400 block mb-1">Speed: {speechRate}x</label>
                                                        <input
                                                            type="range" min="0.5" max="2" step="0.1"
                                                            value={speechRate}
                                                            onChange={(e) => setSpeechRate(parseFloat(e.target.value))}
                                                            className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="text-xs text-gray-400 block mb-1">Volume</label>
                                                        <input
                                                            type="range" min="0" max="1" step="0.1"
                                                            value={speechVolume}
                                                            onChange={(e) => setSpeechVolume(parseFloat(e.target.value))}
                                                            className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                                                        />
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <button
                                    onClick={onSaveGesture}
                                    className="p-3 rounded-full bg-bolt-surface hover:bg-bolt-surface/80 border border-bolt-border text-green-500 transition-colors tooltip"
                                    title="Save to History"
                                >
                                    <Save size={24} />
                                </button>
                                <button
                                    onClick={onClearGesture}
                                    className="p-3 rounded-full bg-bolt-surface hover:bg-bolt-surface/80 border border-bolt-border text-gray-400 hover:text-red-500 transition-colors"
                                    title="Clear"
                                >
                                    <Trash2 size={24} />
                                </button>
                            </div>
                        )}
                    </div>

                </div>
            </div>
        </div>
    );
};

export default HandGestureInterface;
