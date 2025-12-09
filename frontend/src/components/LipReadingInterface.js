import React, { useState, useRef, useEffect } from 'react';
import { Camera, Maximize, Minimize, Play, Square, Volume2, VolumeX, Settings, Download, Trash2, Copy, Loader2, Mic, Pause, Save, Hand } from 'lucide-react';

const LipReadingInterface = ({
    isLive,
    isProcessing,
    onStartLive,
    onStopLive,
    transcribedText,
    confidence,
    onSaveText,
    onClearText,
    useServerVideo,
    videoRef,
    onOpenGestures
}) => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [isVideoLoaded, setIsVideoLoaded] = useState(false);
    const [videoUrl, setVideoUrl] = useState("http://127.0.0.1:5000/video_feed");

    // Reset video loaded state and update URL cache-buster when switching video source
    useEffect(() => {
        setIsVideoLoaded(false);
        if (useServerVideo) {
            setVideoUrl(`http://127.0.0.1:5000/video_feed?t=${Date.now()}`);
        }
    }, [useServerVideo]);

    // Safety: If we receive text, the backend is definitely working, so hide the loader
    useEffect(() => {
        if (transcribedText) setIsVideoLoaded(true);
    }, [transcribedText]);

    const handleVideoLoad = () => {
        setIsVideoLoaded(true);
    };

    // TTS State
    const [speechRate, setSpeechRate] = useState(1);
    const [speechVolume, setSpeechVolume] = useState(1);
    const [showSettings, setShowSettings] = useState(false);

    const speakText = () => {
        if (!transcribedText) return;
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(transcribedText);
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
                    <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">Lip Reading</h2>
                    <p className="text-sm text-bolt-text-secondary">AI-powered visual speech recognition</p>
                </div>
                <div className="flex space-x-2">
                    <button
                        onClick={onOpenGestures}
                        className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-bolt-surface hover:bg-bolt-surface/80 text-gray-400 hover:text-white transition-colors border border-bolt-border hover:border-bolt-primary/50"
                        title="Open Gesture Control"
                    >
                        <Hand size={18} />
                        <span className="text-sm font-medium hidden sm:inline">Gestures</span>
                    </button>
                    <button
                        onClick={toggleFullscreen}
                        className="p-2 rounded-lg bg-bolt-surface hover:bg-bolt-surface/80 text-gray-400 hover:text-white transition-colors"
                    >
                        {isFullscreen ? <Minimize size={20} /> : <Maximize size={20} />}
                    </button>
                </div>
            </div>

            {/* Main Content Area - Split View on Desktop */}
            <div className="flex flex-col lg:flex-row gap-6 flex-grow">

                {/* Video Feed Section */}
                <div className="flex-1 flex flex-col min-h-[300px] lg:min-h-0 bg-black rounded-2xl overflow-hidden relative shadow-2xl ring-1 ring-bolt-border group">

                    {/* Video Element */}
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
                        {useServerVideo ? (
                            <img
                                src={videoUrl}
                                alt="Live Stream"
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

                        {/* Loading / Inactive Overlay */}
                        {(isProcessing || (useServerVideo && !isVideoLoaded) || (!isLive && !useServerVideo)) && (
                            <div className="absolute inset-0 flex items-center justify-center bg-black/80 backdrop-blur-sm z-10">
                                {isProcessing || (useServerVideo && !isVideoLoaded) ? (
                                    <div className="text-center text-bolt-primary animate-in fade-in zoom-in duration-300">
                                        <Loader2 size={48} className="mx-auto mb-4 animate-spin" />
                                        <p className="text-lg font-medium">Starting Engine...</p>
                                        <p className="text-xs text-bolt-text-secondary mt-2">Connecting to neural core</p>
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

                    {/* Overlay Controls */}
                    <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/90 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-20">
                        <div className="flex justify-center space-x-4">
                            {!isLive ? (
                                <button
                                    onClick={onStartLive}
                                    className="flex items-center space-x-2 px-6 py-3 rounded-full bg-bolt-primary hover:bg-bolt-primary/90 text-white font-bold shadow-lg shadow-bolt-primary/20 transform hover:scale-105 transition-all"
                                >
                                    <Play size={20} fill="currentColor" />
                                    <span>Start Session</span>
                                </button>
                            ) : (
                                <button
                                    onClick={onStopLive}
                                    className="flex items-center space-x-2 px-6 py-3 rounded-full bg-red-500 hover:bg-red-600 text-white font-bold shadow-lg shadow-red-500/20 transform hover:scale-105 transition-all"
                                >
                                    <Square size={20} fill="currentColor" />
                                    <span>Stop Session</span>
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Live Indicator */}
                    {isLive && (
                        <div className="absolute top-4 left-4 flex items-center space-x-2 px-3 py-1 rounded-full bg-red-500/20 backdrop-blur-md border border-red-500/30">
                            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                            <span className="text-xs font-bold text-red-500 uppercase tracking-wider">Live</span>
                        </div>
                    )}
                </div>

                {/* Transcription Section */}
                <div className="flex-1 flex flex-col glass-panel rounded-2xl p-1 overflow-hidden">
                    <div className="flex items-center justify-between p-4 border-b border-bolt-border bg-black/20">
                        <div className="flex items-center space-x-2">
                            <Mic size={18} className="text-bolt-primary" />
                            <span className="font-medium text-gray-200">Transcription</span>
                        </div>

                        {/* Confidence Badge */}
                        <div className="text-xs font-mono text-gray-500">
                            Confidence: <span className={confidence > 80 ? 'text-green-500' : 'text-yellow-500'}>{confidence}%</span>
                        </div>
                    </div>

                    {/* Text Display Area */}
                    <div className="flex-grow p-6 overflow-y-auto min-h-[200px] relative">
                        {transcribedText ? (
                            <div className="prose prose-invert max-w-none">
                                <p className="text-xl sm:text-2xl leading-relaxed text-bolt-text-primary animate-in fade-in">
                                    {transcribedText}
                                </p>
                            </div>
                        ) : (
                            <div className="h-full flex items-center justify-center text-gray-600 text-sm">
                                Waiting for speech...
                            </div>
                        )}
                    </div>

                    {/* Action Toolbar */}
                    <div className="bg-black/40 backdrop-blur-md border-t border-bolt-border p-4">
                        <div className="flex flex-wrap items-center gap-2 justify-between">

                            <div className="flex items-center space-x-2">
                                <button
                                    onClick={isPlaying ? stopSpeech : speakText}
                                    disabled={!transcribedText}
                                    className="p-2 rounded-lg hover:bg-white/10 text-gray-300 disabled:opacity-30 transition-colors tooltip"
                                    title="Text to Speech"
                                >
                                    {isPlaying ? <Pause size={20} /> : <Volume2 size={20} />}
                                </button>

                                <div className="relative">
                                    <button
                                        onClick={() => setShowSettings(!showSettings)}
                                        className={`p-2 rounded-lg hover:bg-white/10 text-gray-300 transition-colors ${showSettings ? 'bg-white/10 text-white' : ''}`}
                                    >
                                        <Settings size={20} />
                                    </button>
                                    {/* TTS Settings Dropdown */}
                                    {showSettings && (
                                        <div className="absolute bottom-full left-0 mb-2 w-48 bg-bolt-surface border border-bolt-border rounded-xl p-4 shadow-xl z-20 animate-in slide-in-from-bottom-2">
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

                            <div className="flex items-center space-x-2">
                                <button
                                    onClick={onSaveText}
                                    disabled={!transcribedText}
                                    className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-green-500/10 text-green-500 hover:bg-green-500/20 disabled:opacity-30 disabled:cursor-not-allowed transition-colors font-medium text-sm"
                                >
                                    <Save size={16} />
                                    <span>Save</span>
                                </button>
                                <button
                                    onClick={onClearText}
                                    disabled={!transcribedText}
                                    className="p-2 rounded-lg hover:bg-red-500/10 text-gray-400 hover:text-red-500 disabled:opacity-30 transition-colors"
                                >
                                    <Trash2 size={18} />
                                </button>
                            </div>

                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LipReadingInterface;
