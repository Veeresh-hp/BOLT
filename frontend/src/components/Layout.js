import React from 'react';
import Navbar from './Navbar';

const Layout = ({ children, currentPage, onNavigate, onOpenHistory }) => {
    return (
        <div className="min-h-screen bg-bolt-background text-bolt-text-primary relative overflow-x-hidden">
            {/* Background Ambience */}
            {/* Background Ambience - Enhanced */}
            <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden select-none">
                {/* Animated Gradient Orbs */}
                <div className="absolute top-20 left-20 w-96 h-96 bg-gradient-to-r from-orange-500/20 to-amber-500/20 rounded-full blur-3xl animate-pulse"></div>
                <div className="absolute bottom-20 right-20 w-80 h-80 bg-gradient-to-r from-orange-400/15 to-yellow-500/15 rounded-full blur-3xl animate-pulse delay-1000"></div>
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-72 h-72 bg-gradient-to-r from-amber-500/10 to-orange-600/10 rounded-full blur-3xl animate-pulse delay-2000"></div>

                {/* Additional floating orbs for depth */}
                <div className="absolute top-40 right-1/4 w-32 h-32 bg-gradient-to-r from-amber-400/25 to-orange-400/25 rounded-full blur-2xl animate-float"></div>
                <div className="absolute bottom-40 left-1/3 w-28 h-28 bg-gradient-to-r from-orange-300/20 to-yellow-400/20 rounded-full blur-2xl animate-float-delay"></div>

                {/* Advanced Geometric patterns */}
                <div className="absolute top-32 right-32 w-64 h-64 border border-orange-500/20 rounded-lg transform rotate-45 animate-slow-spin"></div>
                <div className="absolute bottom-32 left-32 w-48 h-48 border-2 border-dashed border-orange-400/30 rounded-full animate-spin-reverse"></div>

                {/* Hexagonal tech pattern */}
                <div className="absolute top-16 left-1/2 w-40 h-40 transform -translate-x-1/2">
                    <div className="w-full h-full border-2 border-amber-500/25 transform rotate-0 animate-pulse" style={{
                        clipPath: 'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)'
                    }}></div>
                </div>

                {/* Floating rectangles with different rotations */}
                <div className="absolute top-1/4 left-16 w-16 h-32 bg-gradient-to-b from-orange-500/10 to-transparent transform rotate-12 animate-float"></div>
                <div className="absolute top-2/3 right-16 w-12 h-24 bg-gradient-to-t from-amber-500/15 to-transparent transform -rotate-12 animate-float-delay"></div>

                {/* Circuit-like connections */}
                <div className="absolute top-1/3 left-1/4 w-32 h-2 bg-gradient-to-r from-orange-500/30 to-transparent animate-pulse"></div>
                <div className="absolute top-1/3 left-1/4 w-2 h-32 bg-gradient-to-b from-orange-500/30 to-transparent animate-pulse delay-500"></div>
                <div className="absolute bottom-1/3 right-1/4 w-32 h-2 bg-gradient-to-l from-amber-500/30 to-transparent animate-pulse delay-1000"></div>
                <div className="absolute bottom-1/3 right-1/4 w-2 h-24 bg-gradient-to-t from-amber-500/25 to-transparent animate-pulse delay-1500"></div>

                {/* Curved decorative elements */}
                <div className="absolute top-1/4 right-1/3 w-64 h-64 border border-orange-400/15 rounded-full animate-spin-slow"></div>
                <div className="absolute bottom-1/4 left-1/3 w-48 h-48 border-2 border-dashed border-amber-400/20 rounded-full animate-spin-reverse-slow"></div>

                {/* Tech grid overlay */}
                <div className="absolute inset-0 opacity-[0.02]" style={{
                    backgroundImage: `radial-gradient(circle at 1px 1px, orange 1px, transparent 0)`,
                    backgroundSize: '40px 40px'
                }}></div>

                {/* Enhanced diagonal pattern */}
                <div className="absolute inset-0 opacity-[0.03]" style={{
                    backgroundImage: `repeating-linear-gradient(45deg, transparent, transparent 50px, orange 50px, orange 51px)`
                }}></div>

                {/* Additional mesh pattern */}
                <div className="absolute inset-0 opacity-[0.015]" style={{
                    backgroundImage: `repeating-linear-gradient(0deg, transparent, transparent 60px, #F59E0B 60px, #F59E0B 61px), 
                           repeating-linear-gradient(90deg, transparent, transparent 60px, #F59E0B 60px, #F59E0B 61px)`
                }}></div>

                {/* Particle-like dots */}
                <div className="absolute top-[20%] left-[20%] w-2 h-2 bg-orange-400/40 rounded-full animate-ping"></div>
                <div className="absolute top-[40%] right-[20%] w-2 h-2 bg-amber-400/40 rounded-full animate-ping delay-1000"></div>
                <div className="absolute bottom-[20%] left-[40%] w-2 h-2 bg-orange-500/40 rounded-full animate-ping delay-2000"></div>
                <div className="absolute bottom-[40%] right-[40%] w-2 h-2 bg-amber-500/40 rounded-full animate-ping delay-3000"></div>

                {/* Glowing accent lines */}
                <div className="absolute top-0 left-1/4 w-1 h-full bg-gradient-to-b from-transparent via-orange-500/10 to-transparent"></div>
                <div className="absolute top-1/4 right-0 w-full h-1 bg-gradient-to-r from-transparent via-amber-500/10 to-transparent"></div>
            </div>

            <Navbar
                currentPage={currentPage}
                onNavigate={onNavigate}
                onOpenHistory={onOpenHistory}
            />

            <main className="relative z-10 pt-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto flex flex-col min-h-[calc(100vh-80px)]">
                {children}
            </main>
        </div>
    );
};

export default Layout;
