'use client';

import React, { useMemo, useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface AvatarProps {
    isTyping: boolean;
    isResponding: boolean;
    mousePos: { x: number; y: number };
    isIdle?: boolean;
    emotion?: string;
    hasAlert?: boolean;
}

const Avatar: React.FC<AvatarProps> = ({ isTyping, isResponding, mousePos, isIdle, emotion = 'neutral', hasAlert }) => {
    const [mounted, setMounted] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const springProps = { type: "spring", stiffness: 120, damping: 12, mass: 0.8 } as const;
    const isWorking = isIdle && !isTyping && !isResponding;

    const [relativePos, setRelativePos] = useState({ x: 0.5, y: 0.5, distance: 1000 });

    useEffect(() => {
        setMounted(true);
    }, []);

    // Localize mouse position to the Avatar container
    useEffect(() => {
        if (!mounted || !containerRef.current) return;
        const rect = containerRef.current.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        
        const dx = mousePos.x - centerX;
        const dy = mousePos.y - centerY;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        // Normalized relative position (-1 to 1)
        setRelativePos({
            x: dx / (window.innerWidth / 2),
            y: dy / (window.innerHeight / 2),
            distance
        });
    }, [mousePos, mounted]);

    const proximity = useMemo(() => {
        return Math.max(0, 1 - relativePos.distance / 300); // 1.0 at center, 0 at 300px
    }, [relativePos.distance]);

    const browPaths = {
        neutral: { L: "M25 38 Q 35 38 43 38", R: "M75 38 Q 65 38 57 38" },
        serious: { L: "M25 38 Q 35 37 43 36", R: "M75 38 Q 65 37 57 36" }, // Flat, less aggressive
        cautious: { L: "M25 34 Q 35 35 43 38", R: "M75 34 Q 65 35 57 38" }, // Softened
        analytical: { L: "M25 36 Q 35 34 43 36", R: "M75 36 Q 65 34 57 36" } // Less steep slant
    };

    const activeEmotion = useMemo(() => {
        if (isTyping) return 'analytical';
        if (proximity > 0.6) return 'serious'; // Looks intensely when close
        if (hasAlert && isWorking) return 'serious';
        return emotion;
    }, [isTyping, hasAlert, isWorking, emotion, proximity]);

    const currentBrows = (browPaths as any)[activeEmotion] || browPaths.neutral;

    const glowColor = useMemo(() => {
        if (proximity > 0.8) return '#ff0000'; // Pure Red when hyper-close
        switch (activeEmotion) {
            case 'serious': return '#ff4d4d';
            case 'analytical': return '#bd00ff';
            default: return '#ffffff';
        }
    }, [activeEmotion, proximity]);

    const parallax = useMemo(() => {
        if (!mounted) return { head: {}, eyes: {}, pupils: {} };
        
        // Base targets
        let targetX = relativePos.x;
        let targetY = relativePos.y;

        // "Idle" floating if not interacting
        if (isWorking && proximity < 0.2) {
            targetX = Math.sin(Date.now() * 0.001) * 0.05;
            targetY = -0.1;
        }

        // Proximity amplification: moves more intensely as cursor nears
        const amp = 1 + proximity * 1.5;

        return {
            head: { 
                x: targetX * 5 * amp, 
                y: targetY * 5 * amp, 
                rotateX: -targetY * 15 * amp, 
                rotateY: targetX * 15 * amp 
            },
            eyes: { x: targetX * 10 * amp, y: targetY * 10 * amp },
            pupils: { x: targetX * 12 * amp, y: targetY * 12 * amp } // Faster pupil tracking
        };
    }, [relativePos, isWorking, proximity, mounted]);

    // Background Data Rain Effect (unchanged logic, refactored for readability)
    useEffect(() => {
        if (!isWorking || !canvasRef.current) return;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let animationFrame: number;
        const particles: any[] = [];
        const codeSnips = ["def audit():", "ptr->0x7f", "async {", "relink()"];

        canvas.width = 160;
        canvas.height = 160;

        class HackingParticle {
            x = Math.random() * 160;
            y = Math.random() * 160;
            speed = 0.5 + Math.random() * 2;
            char = codeSnips[Math.floor(Math.random() * codeSnips.length)];
            opacity = 0;

            draw() {
                if (!ctx) return;
                ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
                ctx.font = '6px monospace';
                ctx.fillText(this.char, this.x, this.y);
                this.y -= this.speed;
                this.opacity = Math.sin(Date.now() * 0.005 + this.x) * 0.2;
                if (this.y < -10) this.y = 170;
            }
        }

        for (let i = 0; i < 10; i++) particles.push(new HackingParticle());
        const animate = () => {
            ctx.clearRect(0, 0, 160, 160);
            particles.forEach(p => p.draw());
            animationFrame = requestAnimationFrame(animate);
        };
        animate();
        return () => cancelAnimationFrame(animationFrame);
    }, [isWorking]);

    const isHovered = relativePos.distance < 40;

    return (
        <div ref={containerRef} className="relative [perspective:1000px] w-40 h-40">
            {/* Background Data Rain */}
            <canvas
                ref={canvasRef}
                className={`absolute top-0 left-0 pointer-events-none z-0 transition-opacity duration-1000 ${isWorking ? 'opacity-40' : 'opacity-0'}`}
                style={{ width: '160px', height: '160px' }}
            />

            <motion.svg
                viewBox="0 0 100 100"
                className="w-full h-full relative z-10"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{
                    ...parallax.head,
                    opacity: 1,
                    scale: isHovered ? [1, 1.02, 0.99, 1] : 1, // Subtle glitch pulse
                    filter: isHovered ? `drop-shadow(0 0 8px ${glowColor})` : 'none'
                }}
                transition={{
                    opacity: { duration: 0.8, ease: "easeOut" },
                    scale: { duration: 0.5, ease: "easeOut" },
                    default: isHovered ? { duration: 0.1, repeat: Infinity } : springProps
                }}
            >
                <defs>
                    <filter id="eye-glow" x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation={1 + proximity * 2} result="blur" />
                        <feComposite in="SourceGraphic" in2="blur" operator="over" />
                    </filter>

                    <radialGradient id="soulGradient" cx="50%" cy="40%" r="60%">
                        <stop offset="0%" stopColor="#2a2a2a" />
                        <stop offset="70%" stopColor="#0a0a0a" />
                        <stop offset="100%" stopColor="#000000" />
                    </radialGradient>
                </defs>

                {/* Main Head Form */}
                <path
                    d="M50 10 C 20 10 15 40 15 60 C 15 85 35 95 50 95 C 65 95 85 85 85 60 C 85 40 80 10 50 10"
                    fill="url(#soulGradient)"
                    stroke={glowColor}
                    strokeWidth={0.2 + proximity * 0.5}
                    style={{ transition: 'stroke 0.3s ease' }}
                />

                {/* Brows */}
                <motion.g initial={false} animate={{ opacity: isWorking ? 0.3 : 1 }}>
                    <motion.path
                        d={currentBrows.L}
                        fill="none"
                        stroke="rgba(255,255,255,0.4)"
                        strokeWidth="1.2"
                        strokeLinecap="round"
                        animate={{ d: currentBrows.L }}
                        transition={springProps}
                    />
                    <motion.path
                        d={currentBrows.R}
                        fill="none"
                        stroke="rgba(255,255,255,0.4)"
                        strokeWidth="1.2"
                        strokeLinecap="round"
                        animate={{ d: currentBrows.R }}
                        transition={springProps}
                    />
                </motion.g>

                {/* Eyes Section */}
                <motion.g animate={parallax.eyes} transition={springProps}>
                    {/* Left Eye */}
                    <g transform="translate(35, 45)">
                        <circle r="8" fill="rgba(0,0,0,0.9)" />
                        <motion.circle
                            animate={parallax.pupils}
                            r={isHovered ? 3.5 : (2 + proximity * 1.2)} // Reduced proximity amplification
                            fill={glowColor}
                            style={{ filter: 'url(#eye-glow)' }}
                            transition={springProps}
                        />
                    </g>
                    {/* Right Eye */}
                    <g transform="translate(65, 45)">
                        <circle r="8" fill="rgba(0,0,0,0.9)" />
                        <motion.circle
                            animate={parallax.pupils}
                            r={isHovered ? 3.5 : (2 + proximity * 1.2)} // Reduced proximity amplification
                            fill={glowColor}
                            style={{ filter: 'url(#eye-glow)' }}
                            transition={springProps}
                        />
                    </g>
                </motion.g>

                {/* Interactive Mouth */}
                <motion.path
                    d={isHovered ? "M40 78 Q 50 82 60 78" : "M42 75 Q 50 76 58 75"}
                    fill="none"
                    stroke={isResponding ? "#fff" : "rgba(255,255,255,0.3)"}
                    strokeWidth={isResponding ? 2 : 1}
                    animate={{
                        d: isHovered ? "M40 78 Q 50 82 60 78" : isResponding ? "M30 75 Q 50 85 70 75" : "M42 75 Q 50 76 58 75",
                        opacity: isResponding ? [0.5, 1, 0.5] : 1
                    }}
                    transition={{ duration: 0.5 }}
                />

                {/* Aura Pulse */}
                <motion.circle
                    cx="50" cy="50" r="46"
                    fill="none"
                    stroke={glowColor}
                    strokeWidth={0.1 + proximity * 0.8}
                    animate={{
                        scale: isHovered ? [1, 1.05, 1] : [1, 1.02, 1],
                        opacity: [0.1, 0.2 + proximity * 0.3, 0.1]
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                />
            </motion.svg>
        </div>
    );
};

export default Avatar;
