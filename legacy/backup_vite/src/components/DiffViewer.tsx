import React from 'react';

interface DiffViewerProps {
    oldCode: string;
    newCode: string;
    fileName: string;
}

const tokenize = (line: string) => {
    const keywords = ['def', 'class', 'import', 'from', 'return', 'if', 'else', 'elif', 'async', 'await', 'try', 'except'];
    const parts = line.split(/(\s+)/);
    return parts.map((part, i) => {
        if (keywords.includes(part.trim())) {
            return <span key={i} className="token-keyword">{part}</span>;
        }
        if (part.trim().startsWith('#')) {
            return <span key={i} className="token-comment">{part}</span>;
        }
        return <span key={i}>{part}</span>;
    });
};

const DiffViewer: React.FC<DiffViewerProps> = ({ oldCode, newCode, fileName }) => {
    const oldLines = oldCode.split('\n');
    const newLines = newCode.split('\n');

    return (
        <div className="diff-viewer">
            <div className="diff-header">
                <div className="diff-title">Architectural Optimization: {fileName}</div>
                <div className="diff-badges">
                    <span className="diff-badge delta">+{newLines.length - oldLines.length} lines</span>
                </div>
            </div>
            <div className="diff-grid">
                <div className="diff-column">
                    <div className="column-label">Legacy Strategy</div>
                    <div className="code-container">
                        {oldLines.map((line, i) => (
                            <div key={i} className="code-line">
                                <span className="line-number">{i + 1}</span>
                                <span className="line-content">{tokenize(line)}</span>
                            </div>
                        ))}
                    </div>
                </div>
                <div className="diff-column">
                    <div className="column-label">Optimized Architecture</div>
                    <div className="code-container">
                        {newLines.map((line, i) => {
                            const isNew = !oldLines.some(l => l.trim() === line.trim());
                            return (
                                <div key={i} className={`code-line ${isNew ? 'line-added' : ''}`}>
                                    <span className="line-number">{i + 1}</span>
                                    <span className="line-content">{tokenize(line)}</span>
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
