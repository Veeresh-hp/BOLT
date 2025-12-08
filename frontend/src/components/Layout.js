import React from 'react';
import Navbar from './Navbar';

const Layout = ({ children, currentPage, onNavigate, onOpenHistory }) => {
    return (
        <div className="min-h-screen bg-bolt-background text-bolt-text-primary relative overflow-x-hidden">
            {/* Background Ambience */}
            <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
                {/* Animated Orbs */}
                <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-bolt-primary/10 blur-[100px] animate-pulse-slow"></div>
                <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] rounded-full bg-bolt-accent/10 blur-[100px] animate-pulse-slow delay-1000"></div>
                <div className="absolute top-[20%] right-[20%] w-[300px] h-[300px] rounded-full bg-bolt-secondary/5 blur-[80px] animate-float"></div>

                {/* Grid Pattern Overlay */}
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-150 contrast-150 mix-blend-overlay"></div>
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
