import React from 'react';
import { Users, Target, Shield, Zap, Cpu, Globe } from 'lucide-react';

const About = () => {
    return (
        <div className="flex flex-col items-center justify-center flex-grow p-6 animate-in fade-in zoom-in duration-500">
            <div className="max-w-4xl w-full space-y-12">

                {/* Header */}
                <div className="text-center space-y-4">
                    <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-bolt-primary to-bolt-accent">
                        About BOLT
                    </h1>
                    <p className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
                        BOLT represents the cutting-edge fusion of artificial intelligence and computer vision technology, designed to revolutionize communication accessibility through advanced lip reading capabilities.
                    </p>
                </div>

                {/* Mission & Technology */}
                <div className="grid md:grid-cols-2 gap-8">
                    <div className="glass-panel p-8 rounded-2xl relative overflow-hidden group hover:border-bolt-primary/30 transition-all duration-300">
                        <div className="relative z-10 space-y-4">
                            <h3 className="text-2xl font-bold text-white flex items-center">
                                <div className="p-2 bg-bolt-surface rounded-lg mr-3 group-hover:bg-bolt-primary/20 transition-colors">
                                    <Target className="text-bolt-primary" size={24} />
                                </div>
                                Our Mission
                            </h3>
                            <p className="text-gray-300 leading-relaxed">
                                To break down communication barriers and provide seamless, accurate lip reading technology that empowers individuals with hearing impairments and enhances communication in noisy environments.
                            </p>
                        </div>
                    </div>

                    <div className="glass-panel p-8 rounded-2xl relative overflow-hidden group hover:border-bolt-accent/30 transition-all duration-300">
                        <div className="relative z-10 space-y-4">
                            <h3 className="text-2xl font-bold text-white flex items-center">
                                <div className="p-2 bg-bolt-surface rounded-lg mr-3 group-hover:bg-bolt-accent/20 transition-colors">
                                    <Cpu className="text-bolt-accent" size={24} />
                                </div>
                                Technology
                            </h3>
                            <p className="text-gray-300 leading-relaxed">
                                Powered by state-of-the-art neural networks and real-time computer vision algorithms, BOLT analyzes lip movements with unprecedented accuracy and speed, now featuring integrated text-to-speech capabilities with real-time adjustments.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Core Values / Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="p-6 rounded-xl bg-bolt-surface border border-bolt-border hover:border-bolt-primary/30 transition-colors">
                        <Zap className="text-bolt-primary mb-4" size={32} />
                        <h4 className="text-lg font-bold text-white mb-2">Real-time Analysis</h4>
                        <p className="text-sm text-gray-400">Instant processing of visual speech and hand movements with low latency.</p>
                    </div>
                    <div className="p-6 rounded-xl bg-bolt-surface border border-bolt-border hover:border-bolt-primary/30 transition-colors">
                        <Shield className="text-bolt-primary mb-4" size={32} />
                        <h4 className="text-lg font-bold text-white mb-2">Privacy First</h4>
                        <p className="text-sm text-gray-400">All processing happens locally or securely. Your data never leaves the loop without permission.</p>
                    </div>
                    <div className="p-6 rounded-xl bg-bolt-surface border border-bolt-border hover:border-bolt-primary/30 transition-colors">
                        <Users className="text-bolt-primary mb-4" size={32} />
                        <h4 className="text-lg font-bold text-white mb-2">Accessibility</h4>
                        <p className="text-sm text-gray-400">Designed from the ground up to be inclusive and easy to use for everyone.</p>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default About;
