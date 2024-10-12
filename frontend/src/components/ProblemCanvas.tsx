import { useProblemCanvasHooks } from '@/hooks/problemCanvasHooks.ts';
import { Hint } from '@/types/hint';
import { PageData, Stroke } from '@/types/pageData';
import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import Markdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// import '../styles/kalam_katex.css';
import { Button } from './ui/button';

interface ProblemCanvasProps {
    penType: 'pen' | 'eraser';
    pageData: PageData;
    setPageData: (pageData: PageData) => void;
    addPageData: (stroke: Stroke) => void;
    setCanvas: (canvas: HTMLCanvasElement) => void;
    hint: Hint | null;
}

const ProblemCanvas: React.FC<ProblemCanvasProps> = ({ penType, pageData, setPageData, addPageData, setCanvas, hint }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
    const eraserDisplayRef = useRef<HTMLDivElement>(null);
    const hintRef = useRef<HTMLDivElement>(null);
    useProblemCanvasHooks(canvasRef, eraserDisplayRef, penType, pageData, setPageData, addPageData, overlayCanvasRef);

    useEffect(() => {
        if (canvasRef.current) {
            setCanvas(canvasRef.current);
        }
    }, [canvasRef.current]);

    const [hintText, setHintText] = useState<string>('');

    useEffect(() => {
        setHintText('');
        (async () => {
            if (hint === null) return;
            while (true) {
                let done = false;
                setHintText((prev) => {
                    if (prev.length >= hint.text.length) {
                        done = true;
                    }
                    return hint.text.slice(0, prev.length + 1);
                });
                if (done) break;
                await new Promise((resolve) => setTimeout(resolve, 50));
            }
        })();
    }, [hint]);
    
    return (
        <div className="relative">
            <canvas
                ref={canvasRef}
                className="w-full bg-white border-t border-b border-gray-200 select-none"
                style={{ aspectRatio: 1 / 1.414 }}
            />
            <canvas
                ref={overlayCanvasRef}
                className="w-full absolute top-0 left-0 border-t border-b border-transparent pointer-events-none"
                style={{ aspectRatio: 1 / 1.414 }}
            />
            {
                <div
                    ref={eraserDisplayRef}
                    className="w-[60px] h-[60px] rounded-full border border-gray-300 absolute transform -translate-x-1/2 -translate-y-1/2 pointer-events-none select-none"
                />
            }
            {
                hint && (
                    <>
                        <motion.div
                            key={`${hint.left}-${hint.right}-${hint.top}-${hint.bottom}`}
                            className="absolute pointer-events-none select-none overflow-hidden"
                            initial={{
                                left: window.innerWidth * hint.left - window.innerWidth * 0.15,
                                top: window.innerWidth * 1.414 * hint.top - window.innerWidth * 0.15,
                                width: window.innerWidth * (hint.right - hint.left) + window.innerWidth * 0.2,
                                height: window.innerWidth * 1.414 * (hint.bottom - hint.top) + window.innerWidth * 0.2,
                                opacity: 0.3,
                            }}
                            animate={{
                                left: window.innerWidth * hint.left - window.innerWidth * 0.05,
                                top: window.innerWidth * 1.414 * hint.top - window.innerWidth * 0.05,
                                width: window.innerWidth * (hint.right - hint.left) + window.innerWidth * 0.1,
                                height: window.innerWidth * 1.414 * (hint.bottom - hint.top) + window.innerWidth * 0.1,
                                opacity: 1,
                            }}
                            transition={{
                                duration: 0.5,
                            }}
                        >
                            <div className="w-full h-full flex flex-row justify-between">
                                <div className="h-full flex flex-col justify-between">
                                    <div className="w-4 h-4 border-l-4 border-t-4 border-red-400 rounded-tl-md" />
                                    <div className="w-4 h-4 border-l-4 border-b-4 border-red-400 rounded-bl-md" />
                                </div>
                                <div className="h-full flex flex-col justify-between">
                                    <div className="w-4 h-4 border-r-4 border-t-4 border-red-400 rounded-tr-md" />
                                    <div className="w-4 h-4 border-r-4 border-b-4 border-red-400 rounded-br-md" />
                                </div>
                            </div>
                        </motion.div>
                        <motion.div
                            key={`${hint.left}-${hint.right}-${hint.top}-${hint.bottom}-text`}
                            ref={hintRef}
                            className="absolute p-8 text-black text-2xl word-wrap pointer-events-none select-none break-keep border-2 border-gray-800/80 bg-white/80 rounded-xl opacity-70"
                            style={{
                                transform: `translate(0, -${hintRef.current?.offsetHeight ?? 0}px)`,
                                transition: 'transform 0.5s',
                            }}
                            initial={{
                                left: window.innerWidth * hint.left - window.innerWidth * 0.05,
                                top: window.innerWidth * 1.414 * hint.top - window.innerWidth * 0.05 - 30,
                                width: window.innerWidth * (hint.right - hint.left) + window.innerWidth * 0.1,
                                opacity: 0.0,
                            }}
                            animate={{
                                left: window.innerWidth * hint.left - window.innerWidth * 0.05,
                                top: window.innerWidth * 1.414 * hint.top - window.innerWidth * 0.05 - 30,
                                width: window.innerWidth * (hint.right - hint.left) + window.innerWidth * 0.1,
                                opacity: 1,
                            }}
                            transition={{
                                duration: 0.3,
                                delay: 0.5,
                            }}
                        >
                            <Markdown
                                remarkPlugins={[remarkMath]}
                                rehypePlugins={[rehypeKatex]}
                            >
                                {hintText}
                            </Markdown>
                        </motion.div>
                    </>
                )
            }
            <Button
                variant="ghost"
                className="absolute left-4 bottom-4 opacity-50"
                onClick={() => setPageData({ strokes: [] })}
            >
                Clear
            </Button>
        </div>
    );
};

export default ProblemCanvas;
