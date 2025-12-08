import React from 'react';
import { X, Trash2, Download, Search, FileText, Hand } from 'lucide-react';

const HistoryModal = ({
    isOpen,
    onClose,
    historyItems,
    onDelete,
    onDownload,
    onClearAll
}) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in">
            <div className="bg-bolt-surface w-full max-w-2xl rounded-2xl border border-bolt-border shadow-2xl relative flex flex-col max-h-[85vh]">

                {/* Header */}
                <div className="flex justify-between items-center p-6 border-b border-bolt-border">
                    <div>
                        <h2 className="text-2xl font-bold text-white">History</h2>
                        <p className="text-gray-400 text-sm">{historyItems.length} entries stored</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
                    >
                        <X size={24} />
                    </button>
                </div>

                {/* List */}
                <div className="flex-grow overflow-y-auto p-6 space-y-4">
                    {historyItems.length === 0 ? (
                        <div className="text-center py-12 text-gray-500">
                            <Search size={48} className="mx-auto mb-4 opacity-20" />
                            <p>No history yet. Start a session to generate logs.</p>
                        </div>
                    ) : (
                        historyItems.map((item) => (
                            <div
                                key={item.id}
                                className="group p-4 rounded-xl bg-black/20 border border-bolt-border hover:border-bolt-primary/30 hover:bg-bolt-primary/5 transition-all"
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
                                        <span className="text-xs text-gray-500">{item.timestamp}</span>
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

                                <p className="text-gray-200 text-lg">{item.text}</p>
                            </div>
                        ))
                    )}
                </div>

                {/* Footer */}
                {historyItems.length > 0 && (
                    <div className="p-4 border-t border-bolt-border bg-black/20 rounded-b-2xl flex justify-between">
                        <button
                            onClick={onClearAll}
                            className="text-red-500 text-sm font-medium hover:underline flex items-center"
                        >
                            <Trash2 size={14} className="mr-1" /> Clear All History
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
