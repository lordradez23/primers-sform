import React, { useEffect, useRef } from 'react';

declare global {
    interface Window {
        mermaid: any;
    }
}

interface MermaidProps {
    chart: string;
}

const Mermaid: React.FC<MermaidProps> = ({ chart }) => {
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (window.mermaid && ref.current) {
            window.mermaid.initialize({ startOnLoad: true, theme: 'dark', securityLevel: 'loose' });
            ref.current.removeAttribute('data-processed');
            window.mermaid.contentLoaded();
        }
    }, [chart]);

    return <div className="mermaid" ref={ref}>{chart}</div>;
};

export default Mermaid;
