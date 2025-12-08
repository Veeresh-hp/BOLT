import React, { useState, useEffect } from 'react';
import { Home, History, User, Mail, Menu, X } from 'lucide-react';

const Navbar = ({ currentPage, onNavigate, onOpenHistory }) => {
    const [isScrolled, setIsScrolled] = useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const navItems = [
        { id: 'home', label: 'Home', icon: Home },
        { id: 'history', label: 'History', icon: History, action: onOpenHistory },
        { id: 'about', label: 'About', icon: User },
        { id: 'contact', label: 'Contact', icon: Mail },
    ];

    return (
        <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled
                ? 'bg-bolt-background/80 backdrop-blur-md border-b border-bolt-border py-2'
                : 'bg-transparent py-4 sm:py-6'
            }`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center">
                    {/* Logo */}
                    <div
                        className="flex items-center cursor-pointer transform hover:scale-105 transition-transform"
                        onClick={() => onNavigate('home')}
                    >
                        {/* Placeholder for Logo if image fails, or use text */}
                        <div className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-bolt-primary to-bolt-accent">
                            BOLT
                        </div>
                    </div>

                    {/* Desktop Navigation */}
                    <div className="hidden md:flex items-center space-x-4">
                        {navItems.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => {
                                    if (item.action) item.action();
                                    else onNavigate(item.id);
                                }}
                                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${currentPage === item.id && !item.action
                                        ? 'bg-bolt-primary/20 text-bolt-primary border border-bolt-primary/30'
                                        : 'text-gray-300 hover:text-white hover:bg-white/5'
                                    }`}
                            >
                                <item.icon size={18} />
                                <span>{item.label}</span>
                            </button>
                        ))}
                    </div>

                    {/* Mobile Menu Button */}
                    <div className="md:hidden">
                        <button
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            className="text-gray-300 hover:text-white p-2"
                        >
                            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu Dropdown */}
            {isMobileMenuOpen && (
                <div className="md:hidden bg-bolt-surface border-b border-bolt-border absolute w-full top-full left-0 animate-in slide-in-from-top-2">
                    <div className="px-4 pt-2 pb-4 space-y-1">
                        {navItems.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => {
                                    if (item.action) item.action();
                                    else onNavigate(item.id);
                                    setIsMobileMenuOpen(false);
                                }}
                                className={`flex items-center space-x-3 w-full px-4 py-3 rounded-lg text-left ${currentPage === item.id && !item.action
                                        ? 'bg-bolt-primary/20 text-bolt-primary'
                                        : 'text-gray-300 hover:bg-white/5'
                                    }`}
                            >
                                <item.icon size={20} />
                                <span>{item.label}</span>
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </nav>
    );
};

export default Navbar;
