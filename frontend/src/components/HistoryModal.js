import React, { useState } from 'react';
import { X, Trash2, Download, Search, FileText, Hand, Bookmark, Cloud } from 'lucide-react';

const HistoryModal = ({
    isOpen,
    onClose,
    historyItems,
    onDelete,
    onDownload,
    onClearAll
}) => {
    const [activeTab, setActiveTab] = useState('saved'); // 'saved' | 'history'

    if (!isOpen) return null;

    // Filter items based on tab
    const filteredItems = activeTab === 'saved'
        ? historyItems.filter(item => item.isSaved)
        : historyItems;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in">
            <div className="bg-bolt-surface w-full max-w-2xl rounded-2xl border border-bolt-border shadow-2xl relative flex flex-col max-h-[85vh] overflow-hidden">

                {/* Header */}
                <div className="flex justify-between items-center p-6 border-b border-bolt-border bg-black/20">
                    <div>
                        <h2 className="text-2xl font-bold text-white">Logbook</h2>
                        <p className="text-gray-400 text-sm">Review your session data</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
                    >
                        <X size={24} />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex p-2 gap-2 bg-black/40 border-b border-bolt-border">
                    <button
                        onClick={() => setActiveTab('saved')}
                        className={`flex-1 flex items-center justify-center space-x-2 py-3 rounded-lg text-sm font-medium transition-all duration-300 ${activeTab === 'saved'
                                ? 'bg-bolt-primary/20 text-bolt-primary ring-1 ring-bolt-primary/50 shadow-lg'
                                : 'text-gray-400 hover:text-white hover:bg-white/5'
                            }`}
                    >
                        <Bookmark size={16} />
                        <span>Saved Items</span>
                    </button>
                    <button
                        onClick={() => setActiveTab('history')}
                        className={`flex-1 flex items-center justify-center space-x-2 py-3 rounded-lg text-sm font-medium transition-all duration-300 ${activeTab === 'history'
                                ? 'bg-bolt-primary/20 text-bolt-primary ring-1 ring-bolt-primary/50 shadow-lg'
                                : 'text-gray-400 hover:text-white hover:bg-white/5'
                            }`}
                    >
                        <Cloud size={16} />
                        <span>Full History</span>
                    </button>
                </div>

                {/* Sliding List Container */}
                <div className="flex-grow overflow-y-auto p-6 space-y-4 relative bg-gradient-to-b from-transparent to-black/20">

                    {/* Content */}
                    <div className="animate-in fade-in slide-in-from-bottom-2 duration-300 key={activeTab}">
                        {filteredItems.length === 0 ? (
                            <div className="text-center py-12 text-gray-500">
                                {activeTab === 'saved' ? (
                                    <>
                                        <Bookmark size={48} className="mx-auto mb-4 opacity-20" />
                                        <p>No saved items yet.</p>
                                        <p className="text-xs mt-2">Click the "Save" button during a session to keep it here.</p>
                                    </>
                                ) : (
                                    <>
                                        <Search size={48} className="mx-auto mb-4 opacity-20" />
                                        <p>No history detected.</p>
                                    </>
                                )}
                            </div>
                        ) : (
                            filteredItems.map((item) => (
                                <div
                                    key={item.id}
                                    className={`group p-4 rounded-xl border transition-all ${item.isSaved
                                            ? 'bg-bolt-surface border-bolt-accent/30 hover:border-bolt-accent/60'
                                            : 'bg-black/20 border-bolt-border hover:border-bolt-primary/30'
                                        }`}
                                >
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex items-center space-x-2">
                                            {item.type === 'gesture' ? (
                                                <span className="flex items-center space-x-1 px-2 py-0.5 rounded text-xs font-medium bg-bolt-accent/20 text-bolt-accent border border-bolt-accent/20">
                                                    <Hand size={12} /> <span>Gesture</span>
                                                </span>
                                            ) : (
                                                <span className="flex items-center space-x-1 px-2 py-0.5 rounded text-xs font-medium bg-bolt-primary/20 text-bolt-primary border border-bolt-primary/20">
                                                    <FileText size={12} /> <span>Lip Reading</span>
                                                </span>
                                            )}
                                            {item.isSaved && (
                                                <span className="flex items-center space-x-1 px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-500 border border-green-500/20">
                                                    <Bookmark size={10} /> <span>Saved</span>
                                                </span>
                                            )}
                                            <span className="text-xs text-gray-500 border-l border-gray-700 pl-2 ml-2">{item.timestamp}</span>
                                        </div>

                                        <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button
                                                onClick={() => onDownload(item)}
                                                className="p-1.5 rounded-md hover:bg-white/10 text-gray-400 hover:text-blue-400"
                                                title="Download"
                                            >
                                                <Download size={16} />
                                            </button>
                                            <button
                                                onClick={() => onDelete(item.id)}
                                                className="p-1.5 rounded-md hover:bg-white/10 text-gray-400 hover:text-red-500"
                                                title="Delete"
                                            >
                                                <Trash2 size={16} />
                                            </button>
                                        </div>
                                    </div>

                                    <p className="text-gray-200 text-lg leading-relaxed">{item.text}</p>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Footer */}
                {historyItems.length > 0 && (
                    <div className="p-4 border-t border-bolt-border bg-black/20 flex justify-between">
                        <button
                            onClick={onClearAll}
                            className="text-red-500 text-sm font-medium hover:underline flex items-center hover:bg-red-500/10 px-3 py-2 rounded-lg transition-colors"
                        >
                            <Trash2 size={14} className="mr-2" /> Clear All Data
                        </button>
                        <button
                            onClick={onClose}
                            className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white font-medium text-sm transition-colors"
                        >
                            Close
                        </button>
                    </div>
                )}

            </div>
        </div>
    );
};

export default HistoryModal;
