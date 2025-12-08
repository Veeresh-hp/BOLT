import React from 'react';
import { ArrowRight, Camera, Hand, MessageSquare } from 'lucide-react';

const Home = ({ onStartLipReading, onStartGestures }) => {
    return (
        <div className="flex flex-col items-center justify-center flex-grow text-center py-12 sm:py-20 animate-in fade-in zoom-in duration-500">

            {/* Hero Section */}
            <div className="max-w-4xl mx-auto space-y-8">
                <div className="inline-flex items-center px-4 py-2 rounded-full border border-bolt-border bg-bolt-surface/50 backdrop-blur-sm mb-4">
                    <span className="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></span>
                    <span className="text-sm font-medium text-gray-400">System Online</span>
                </div>

                <h1 className="font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-br from-white via-gray-200 to-gray-500">
                    Transforming Movement <br />
                    <span className="text-bolt-primary">Into Meaning</span>
                </h1>

                <p className="max-w-2xl mx-auto text-lg sm:text-xl text-bolt-text-secondary leading-relaxed">
                    Experience the future of assistive communication. Real-time lip reading and hand gesture recognition powered by advanced AI.
                </p>

                {/* Action Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-12 w-full max-w-3xl px-4">

                    {/* Lip Reading Card */}
                    <div
                        onClick={onStartLipReading}
                        className="group relative overflow-hidden rounded-2xl glass-panel p-8 text-left cursor-pointer transition-all duration-300 hover:translate-y-[-5px] hover:border-bolt-primary/50"
                    >
                        <div className="absolute inset-0 bg-gradient-to-br from-bolt-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                        <div className="relative z-10">
                            <div className="w-12 h-12 rounded-xl bg-bolt-primary/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                <MessageSquare className="text-bolt-primary" size={24} />
                            </div>
                            <h3 className="text-xl font-bold mb-2 text-white">Lip Reading</h3>
                            <p className="text-sm text-gray-400 mb-4">Real-time speech-to-text from visual lip movements.</p>
                            <div className="flex items-center text-bolt-primary font-medium text-sm group-hover:translate-x-1 transition-transform">
                                Start Session <ArrowRight size={16} className="ml-1" />
                            </div>
                        </div>
                    </div>

                    {/* Hand Gestures Card */}
                    <div
                        onClick={onStartGestures}
                        className="group relative overflow-hidden rounded-2xl glass-panel p-8 text-left cursor-pointer transition-all duration-300 hover:translate-y-[-5px] hover:border-bolt-accent/50"
                    >
                        <div className="absolute inset-0 bg-gradient-to-br from-bolt-accent/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                        <div className="relative z-10">
                            <div className="w-12 h-12 rounded-xl bg-bolt-accent/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                <Hand className="text-bolt-accent" size={24} />
                            </div>
                            <h3 className="text-xl font-bold mb-2 text-white">Gesture Control</h3>
                            <p className="text-sm text-gray-400 mb-4">Control interfaces and communicate using hand signs.</p>
                            <div className="flex items-center text-bolt-accent font-medium text-sm group-hover:translate-x-1 transition-transform">
                                Start Detection <ArrowRight size={16} className="ml-1" />
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
};

export default Home;
