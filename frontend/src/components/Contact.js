import React from 'react';
import { Mail, Phone, MapPin, Send } from 'lucide-react';

const Contact = () => {
    return (
        <div className="flex flex-col items-center justify-center flex-grow p-6 animate-in fade-in slide-in-from-bottom-4">
            <div className="max-w-2xl w-full glass-panel rounded-2xl p-8 space-y-8">

                <div className="text-center space-y-2">
                    <h2 className="text-3xl font-bold text-white">Get in Touch</h2>
                    <p className="text-gray-400">We'd love to hear from you. Send us a message!</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Contact Info */}
                    <div className="space-y-6">
                        <div className="flex items-center space-x-4 text-gray-300">
                            <div className="p-3 bg-bolt-surface rounded-lg">
                                <Mail className="text-bolt-primary" size={20} />
                            </div>
                            <div>
                                <p className="text-xs text-gray-500">Email</p>
                                <p className="font-medium">contact@bolt-assistive.com</p>
                            </div>
                        </div>

                        <div className="flex items-center space-x-4 text-gray-300">
                            <div className="p-3 bg-bolt-surface rounded-lg">
                                <Phone className="text-bolt-primary" size={20} />
                            </div>
                            <div>
                                <p className="text-xs text-gray-500">Phone</p>
                                <p className="font-medium">+1 (555) 123-4567</p>
                            </div>
                        </div>

                        <div className="flex items-center space-x-4 text-gray-300">
                            <div className="p-3 bg-bolt-surface rounded-lg">
                                <MapPin className="text-bolt-primary" size={20} />
                            </div>
                            <div>
                                <p className="text-xs text-gray-500">Office</p>
                                <p className="font-medium">123 Innovation Drive, Tech City</p>
                            </div>
                        </div>
                    </div>

                    {/* Form */}
                    <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
                        <div>
                            <label className="block text-xs text-gray-500 mb-1">Name</label>
                            <input
                                type="text"
                                className="w-full bg-black/20 border border-bolt-border rounded-lg px-4 py-2 text-white focus:outline-none focus:border-bolt-primary transition-colors"
                                placeholder="John Doe"
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-gray-500 mb-1">Message</label>
                            <textarea
                                className="w-full bg-black/20 border border-bolt-border rounded-lg px-4 py-2 text-white focus:outline-none focus:border-bolt-primary transition-colors h-24 resize-none"
                                placeholder="How can we help?"
                            ></textarea>
                        </div>
                        <button className="w-full bg-bolt-primary hover:bg-bolt-primary/90 text-white font-bold py-2 rounded-lg transition-colors flex items-center justify-center space-x-2">
                            <Send size={16} />
                            <span>Send Message</span>
                        </button>
                    </form>
                </div>

            </div>
        </div>
    );
};

export default Contact;
