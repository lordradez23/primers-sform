'use client';

import React, { useEffect, useRef, useState } from 'react';

const Mermaid = ({ chart }: { chart: string }) => {
  const ref = useRef<HTMLDivElement>(null);
  const [svg, setSvg] = useState<string>('');
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Dynamically import mermaid to avoid SSR issues
    import('mermaid').then((mermaid) => {
      mermaid.default.initialize({
        startOnLoad: false,
        theme: 'dark' as any,
        securityLevel: 'loose',
        fontFamily: 'Inter, sans-serif',
      });
      setIsLoaded(true);
    });
  }, []);

  useEffect(() => {
    if (isLoaded && ref.current) {
        import('mermaid').then(async (mermaid) => {
            try {
                const id = `mermaid-svg-${Math.random().toString(36).substr(2, 9)}`;
                const { svg: renderedSvg } = await mermaid.default.render(id, chart);
                setSvg(renderedSvg);
            } catch (err) {
                console.error('Mermaid rendering failed:', err);
                setError('Neural blueprint mapping failed. Syntax invalid.');
            }
        });
    }
  }, [chart, isLoaded]);

  if (error) {
    return (
        <div className="bg-red-950/20 border border-red-500/20 rounded-lg p-6 my-4 text-center">
            <p className="text-red-400 text-[10px] font-bold uppercase tracking-widest">{error}</p>
        </div>
    );
  }

  return (
    <div 
        ref={ref} 
        className="mermaid-wrapper bg-black/20 rounded-lg p-4 my-4 border border-white/5 overflow-x-auto flex justify-center"
        dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
};

export default Mermaid;
