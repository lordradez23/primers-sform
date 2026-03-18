'use client';

import React from 'react';

interface DiffViewerProps {
    diff: {
        current_code: string;
        proposed_code: string;
        target_file: string;
    };
    onApply?: () => void;
    isApplying?: boolean;
}

const tokenize = (line: string) => {
    const keywords = ['def', 'class', 'import', 'from', 'return', 'if', 'else', 'elif', 'async', 'await', 'try', 'except'];
    const parts = line.split(/(\s+)/);
    return parts.map((part, i) => {
        if (keywords.includes(part.trim())) {
            return <span key={i} className="text-purple-400 font-bold">{part}</span>;
        }
        if (part.trim().startsWith('#')) {
            return <span key={i} className="text-gray-500 italic">{part}</span>;
        }
        return <span key={i}>{part}</span>;
    });
};

const DiffViewer: React.FC<DiffViewerProps> = ({ diff, onApply, isApplying }) => {
    const { current_code: oldCode, proposed_code: newCode, target_file: fileName } = diff;
    const oldLines = oldCode.split('\n');
    const newLines = newCode.split('\n');

    return (
        <div className="bg-neutral-900/50 border border-white/10 rounded-xl overflow-hidden backdrop-blur-md my-4">
            <div className="bg-white/5 px-4 py-3 border-b border-white/10 flex justify-between items-center">
                <div className="text-sm font-medium text-white/80">Architectural Optimization: <span className="text-white">{fileName}</span></div>
                <div className="flex gap-2">
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-green-500/20 text-green-400 border border-green-500/30">
                        +{newLines.length - oldLines.length} lines
                    </span>
                    {onApply && (
                        <button 
                            onClick={onApply}
                            disabled={isApplying}
                            className="text-[10px] px-3 py-0.5 rounded-full bg-blue-500 hover:bg-blue-600 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isApplying ? 'Applying...' : 'Apply Change'}
                        </button>
                    )}
                </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-white/10">
                <div className="flex flex-col">
                    <div className="px-4 py-2 text-[10px] uppercase tracking-wider text-white/40 bg-white/5 border-b border-white/10 font-bold">Legacy Strategy</div>
                    <div className="p-4 overflow-x-auto font-mono text-xs leading-relaxed max-h-80 overflow-y-auto custom-scrollbar bg-black/20">
                        {oldLines.map((line, i) => (
                            <div key={i} className="flex gap-4 group hover:bg-white/5 px-2 -mx-2 transition-colors">
                                <span className="w-8 text-right text-white/20 select-none group-hover:text-white/40">{i + 1}</span>
                                <span className="whitespace-pre text-white/70">{tokenize(line)}</span>
                            </div>
                        ))}
                    </div>
                </div>
                
                <div className="flex flex-col">
                    <div className="px-4 py-2 text-[10px] uppercase tracking-wider text-green-400/60 bg-green-400/5 border-b border-white/10 font-bold">Optimized Architecture</div>
                    <div className="p-4 overflow-x-auto font-mono text-xs leading-relaxed max-h-80 overflow-y-auto custom-scrollbar bg-black/20">
                        {newLines.map((line, i) => {
                            const isNew = !oldLines.some(l => l.trim() === line.trim());
                            return (
                                <div key={i} className={`flex gap-4 px-2 -mx-2 transition-colors group ${isNew ? 'bg-green-500/10 hover:bg-green-500/20' : 'hover:bg-white/5'}`}>
                                    <span className={`w-8 text-right select-none ${isNew ? 'text-green-400/50 group-hover:text-green-400' : 'text-white/20 group-hover:text-white/40'}`}>
                                        {i + 1}
                                    </span>
                                    <span className={`whitespace-pre ${isNew ? 'text-green-300' : 'text-white/70'}`}>{tokenize(line)}</span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DiffViewer;
