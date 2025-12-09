import React, { useEffect, useRef, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './components/Home';
import LipReadingInterface from './components/LipReadingInterface';
import HandGestureInterface from './components/HandGestureInterface';
import HistoryModal from './components/HistoryModal';
import About from './components/About';
import Contact from './components/Contact';

const AppContent = () => {
  // --- Config ---
  const TOAST_DURATION = 3000;

  // --- Router Hooks ---
  const navigate = useNavigate();
  const location = useLocation();

  // --- UI State ---
  const [useServerVideo, setUseServerVideo] = useState(false);

  // --- Lip Reading State ---
  const [isLipReadingLive, setIsLipReadingLive] = useState(false);
  const [lipReadingProcessing, setLipReadingProcessing] = useState(false);
  const [transcribedText, setTranscribedText] = useState('');
  const [lipReadingConfidence, setLipReadingConfidence] = useState(95);

  // --- Hand Gesture State ---
  const [isGestureLive, setIsGestureLive] = useState(false);
  const [gestureProcessing, setGestureProcessing] = useState(false);
  const [gestureText, setGestureText] = useState('');
  const [gestureConfidence, setGestureConfidence] = useState(0);

  // --- History State ---
  const [allHistory, setAllHistory] = useState([]);
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);

  // --- Refs ---
  const videoRef = useRef(null); // Local video ref
  const streamRef = useRef(null);
  const processingIntervalRef = useRef(null);

  // --- Toasts (Simplified) ---
  const showToast = (msg, type = 'info') => {
    // In a real app we'd use a toast library or custom component
    console.log(`[TOAST ${type}]: ${msg}`);
  };

  // --- Helpers ---
  const addToHistory = (text, type) => {
    setAllHistory(prev => {
      // Prevent duplicates at the top of the stack
      if (prev.length > 0 && prev[0].text === text && prev[0].type === type) return prev;
      return [{
        id: Date.now(),
        text,
        type,
        timestamp: new Date().toLocaleTimeString()
      }, ...prev];
    });
  };

  const deleteHistoryItem = (id) => setAllHistory(prev => prev.filter(i => i.id !== id));
  const clearHistory = () => setAllHistory([]);
  const downloadHistoryItem = (item) => {
    const blob = new Blob([item.text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${item.type}-log-${item.id}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  // --- Camera Management ---
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play().catch(e => console.error(e));
      }
      streamRef.current = stream;
      setUseServerVideo(false);
    } catch (err) {
      console.error('Camera Error:', err);
      // Fallback to server video if local camera fails (or is in use by backend)
      setUseServerVideo(true);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setUseServerVideo(false);
  };

  // --- Lip Reading Logic ---
  const startLipReading = async () => {
    if (isLipReadingLive || processingIntervalRef.current) return;
    setIsLipReadingLive(true);
    setTranscribedText('');

    // Stop local camera so backend can take it
    stopCamera();

    try {
      // 1. Health Check
      const health = await fetch('http://127.0.0.1:5000/');
      if (!health.ok) throw new Error('Backend not running');

      // 2. Start Backend Process
      setLipReadingProcessing(true);
      await fetch('http://127.0.0.1:5000/start_lip_reading');

      // 3. Switch to server video (backend pipe)
      setUseServerVideo(true);

      // 4. Poll for results
      processingIntervalRef.current = setInterval(async () => {
        try {
          const res = await fetch('http://127.0.0.1:5000/latest_result');
          const data = await res.json();
          if (data.type === 'lip-reading' && data.text) {
            setTranscribedText(data.text);
            addToHistory(data.text, 'lip-reading');
          }
        } catch (e) { console.error('Polling error', e); }
      }, 1000);

      // Keep loader visible for a moment while backend warms up
      await new Promise(resolve => setTimeout(resolve, 3000));

    } catch (err) {
      console.error(err);
      showToast('Failed to start Lip Reading', 'error');
      setIsLipReadingLive(false);
      setUseServerVideo(false); // Revert?
    } finally {
      setLipReadingProcessing(false);
    }
  };

  const stopLipReading = async () => {
    setIsLipReadingLive(false);
    setLipReadingProcessing(false);
    if (processingIntervalRef.current) {
      clearInterval(processingIntervalRef.current);
      processingIntervalRef.current = null;
    }
    try {
      await fetch('http://127.0.0.1:5000/stop_lip_reading');
    } catch (e) { console.error(e); }
    setUseServerVideo(false);
  };

  // --- Hand Gesture Logic ---
  const startGestures = async () => {
    if (isGestureLive || processingIntervalRef.current) return;
    setIsGestureLive(true);
    setGestureText('');
    stopCamera(); // Release for backend

    try {
      // 1. Health Check
      const health = await fetch('http://127.0.0.1:5000/');
      if (!health.ok) throw new Error('Backend not running');

      // 2. Start Backend
      setGestureProcessing(true);
      await fetch('http://127.0.0.1:5000/start_hand_gestures');

      // 3. Switch video
      setUseServerVideo(true);

      // 4. Poll
      processingIntervalRef.current = setInterval(async () => {
        try {
          const res = await fetch('http://127.0.0.1:5000/latest_result');
          const data = await res.json();
          if (data.type === 'hand-gesture' && data.text) {
            setGestureText(data.text);
            addToHistory(data.text, 'gesture');
          }
        } catch (e) { console.error('Polling error', e); }
      }, 1000);

      // Keep loader visible for a moment while backend warms up
      await new Promise(resolve => setTimeout(resolve, 3000));

    } catch (err) {
      console.error(err);
      showToast('Failed to start Gestures', 'error');
      setIsGestureLive(false);
      setUseServerVideo(false);
    } finally {
      setGestureProcessing(false);
    }
  };

  const stopGestures = async () => {
    setIsGestureLive(false);
    setGestureProcessing(false);
    if (processingIntervalRef.current) {
      clearInterval(processingIntervalRef.current);
      processingIntervalRef.current = null;
    }
    try {
      await fetch('http://127.0.0.1:5000/stop_hand_gestures');
    } catch (e) { console.error(e); }
    setUseServerVideo(false);
  };

  // --- Auto Cleanup on Route Change ---
  useEffect(() => {
    // Determine which page we are on
    const path = location.pathname;

    // Cleanup Lip Reading if we left the page
    if (path !== '/lip-reading' && isLipReadingLive) {
      stopLipReading();
    }

    // Cleanup Gestures if we left the page
    if (path !== '/hand-gestures' && isGestureLive) {
      stopGestures();
    }

    // Setup Camera for new page if needed (Auto-start local camera)
    // Note: User might prefer manual start, but usually navigating to the page implies intent.
    // However, to keep it stable, let's start camera on mount for these pages.
    if (path === '/lip-reading' || path === '/hand-gestures') {
      startCamera();
    } else {
      stopCamera();
    }

    // Reset video state when navigating
    setUseServerVideo(false);

  }, [location.pathname]); // Dependency on path only, to trigger on navigation

  // --- Navigation Handler for Layout ---
  const handleNavigate = (pageId) => {
    if (pageId === 'home') navigate('/');
    else if (pageId === 'lip-reading') navigate('/lip-reading'); // Mapping checks
    else if (pageId === 'gestures') navigate('/hand-gestures');
    else navigate(`/${pageId}`);
  };

  // Map current path to ID for Layout highlighting
  const getCurrentPageId = () => {
    const path = location.pathname;
    if (path === '/') return 'home';
    if (path === '/lip-reading') return 'lip-reading'; // Navbar doesn't have this link explicitly usually? 
    // Navbar items: home, history, about, contact. 
    // Lip Reading / Gestures are usually via Home cards.
    // But if we want to add them to navbar or just handle highlighting:
    if (path === '/hand-gestures') return 'gestures';
    if (path === '/about') return 'about';
    if (path === '/contact') return 'contact';
    return 'home';
  };

  // --- Helpers ---
  const saveText = () => showToast('Saved text');
  const clearText = () => setTranscribedText('');
  const saveGesture = () => showToast('Saved gesture');
  const clearGesture = () => setGestureText('');

  return (
    <Layout
      currentPage={getCurrentPageId()}
      onNavigate={handleNavigate}
      onOpenHistory={() => setIsHistoryModalOpen(true)}
    >
      <Routes>
        <Route path="/" element={
          <Home
            onStartLipReading={() => navigate('/lip-reading')}
            onStartGestures={() => navigate('/hand-gestures')}
          />
        } />

        <Route path="/lip-reading" element={
          <LipReadingInterface
            isLive={isLipReadingLive}
            isProcessing={lipReadingProcessing}
            onStartLive={startLipReading}
            onStopLive={stopLipReading}
            transcribedText={transcribedText}
            confidence={lipReadingConfidence}
            onSaveText={saveText}
            onClearText={clearText}
            useServerVideo={useServerVideo}
            videoRef={videoRef}
            onOpenGestures={() => navigate('/hand-gestures')}
          />
        } />

        <Route path="/hand-gestures" element={
          <HandGestureInterface
            isLive={isGestureLive}
            isProcessing={gestureProcessing}
            onStartLive={startGestures}
            onStopLive={stopGestures}
            gestureText={gestureText}
            onSaveGesture={saveGesture}
            onClearGesture={clearGesture}
            useServerVideo={useServerVideo}
            videoRef={videoRef}
            onOpenLipReading={() => navigate('/lip-reading')}
          />
        } />

        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      <HistoryModal
        isOpen={isHistoryModalOpen}
        onClose={() => setIsHistoryModalOpen(false)}
        historyItems={allHistory}
        onDelete={deleteHistoryItem}
        onDownload={downloadHistoryItem}
        onClearAll={clearHistory}
      />
    </Layout>
  );
};

const App = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;