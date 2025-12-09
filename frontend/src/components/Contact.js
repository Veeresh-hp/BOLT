import React from 'react';
import { Mail, Users, Camera, Send, User } from 'lucide-react';

const Contact = () => {
    return (
        <div className="flex flex-col items-center justify-center flex-grow p-4 sm:p-6 animate-in fade-in slide-in-from-bottom-4">

            <h1 className="text-4xl font-bold mb-8 text-white">
                Contact <span className="text-bolt-primary">Us</span>
            </h1>

            <div className="max-w-5xl w-full glass-panel rounded-2xl p-8 md:p-10">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-12">

                    {/* Left Column: Info */}
                    <div className="space-y-8">
                        <div>
                            <h2 className="text-2xl font-bold text-white mb-4">Get in Touch</h2>
                            <p className="text-gray-400 leading-relaxed">
                                Have questions about BOLT (Breaking Obstacles with Lip-reading Technology) or want to learn more about our assistive communication system? We'd love to hear from you.
                            </p>
                        </div>

                        <div className="space-y-5">
                            <div className="flex items-center space-x-4 text-gray-300">
                                <Mail className="text-bolt-primary" size={20} />
                                <span className="font-medium">bolt@sjbit.edu.in</span>
                            </div>

                            <div className="flex items-center space-x-4 text-gray-300">
                                <Users className="text-bolt-primary" size={20} />
                                <span className="font-medium">SJB Institute of Technology Team</span>
                            </div>

                            <div className="flex items-center space-x-4 text-gray-300">
                                <Camera className="text-bolt-primary" size={20} />
                                <span className="font-medium">VTU Project 2025-26</span>
                            </div>
                        </div>

                        {/* Project Team Card */}
                        <div className="bg-bolt-surface/50 rounded-xl p-5 border border-bolt-border/50">
                            <h3 className="text-white font-semibold mb-3">Project Team</h3>
                            <ul className="space-y-1 text-sm text-gray-400">
                                <li>Sudeeksha T [1JB22IS157]</li>
                                <li>T J Shashank [1JB22IS164]</li>
                                <li>Tanusha Urs M [1JB22IS165]</li>
                                <li>Veeresh H P [1JB22IS180]</li>
                            </ul>
                            <p className="text-bolt-primary text-sm mt-3 font-medium">
                                Under guidance of Prof. Gayathri G
                            </p>
                        </div>
                    </div>

                    {/* Right Column: Form */}
                    <div>
                        <form className="space-y-5" onSubmit={(e) => e.preventDefault()}>
                            <div>
                                <input
                                    type="text"
                                    className="w-full bg-black/20 border border-bolt-border rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-bolt-primary transition-colors"
                                    placeholder="Your Name"
                                />
                            </div>
                            <div>
                                <input
                                    type="email"
                                    className="w-full bg-black/20 border border-bolt-border rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-bolt-primary transition-colors"
                                    placeholder="Your Email"
                                />
                            </div>
                            <div>
                                <textarea
                                    className="w-full bg-black/20 border border-bolt-border rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-bolt-primary transition-colors h-40 resize-none"
                                    placeholder="Your Message"
                                ></textarea>
                            </div>
                            <button className="w-full bg-bolt-primary hover:bg-bolt-primary/90 text-white font-bold py-3 rounded-lg transition-colors shadow-lg shadow-bolt-primary/20">
                                Send Message
                            </button>
                        </form>
                    </div>

                </div>
            </div>
        </div>
    );
};

export default Contact;
