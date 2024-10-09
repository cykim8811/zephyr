import { useProblemCanvasHooks } from '@/hooks/problemCanvasHooks.ts';
import { Hint } from '@/types/hint';
import { PageData, Stroke } from '@/types/pageData';
import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import Markdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

import '../styles/kalam_katex.css';
import { Button } from './ui/button';

interface ProblemCanvasProps {
    penType: 'pen' | 'eraser';
    pageData: PageData;
    setPageData: (pageData: PageData) => void;
    addPageData: (stroke: Stroke) => void;
    setCanvas: (canvas: HTMLCanvasElement) => void;
    hints: Hint[];
}

const ProblemCanvas: React.FC<ProblemCanvasProps> = ({ penType, pageData, setPageData, addPageData, setCanvas, hints }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
    const eraserDisplayRef = useRef<HTMLDivElement>(null);
    useProblemCanvasHooks(canvasRef, eraserDisplayRef, penType, pageData, setPageData, addPageData, overlayCanvasRef);

    useEffect(() => {
        if (canvasRef.current) {
            setCanvas(canvasRef.current);
        }
    }, [canvasRef.current]);


    // useEffect(() => {
    //     setHintText('');
    //     (async () => {
    //         if (hint === null) return;
    //         while (true) {
    //             let done = false;
    //             setHintText((prev) => {
    //                 if (prev.length >= hint.text.length) {
    //                     done = true;
    //                 }
    //                 return hint.text.slice(0, prev.length + 1);
    //             });
    //             if (done) break;
    //             await new Promise((resolve) => setTimeout(resolve, 50));
    //         }
    //     })();
    // }, [hint]);
    
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
                hints.map((hint) =>
                    <div
                        key={`${hint.left}-${hint.right}-${hint.top}-${hint.bottom}-container`}
                        className="absolute border border-gray-300 p-2"
                        style={{
                            left: `${hint.left * 100}%`,
                            right: `${(1 - hint.right) * 100}%`,
                            top: `${hint.top * 100}%`,
                            bottom: `${(1 - hint.bottom) * 100}%`,
                        }}
                    >

                        <Markdown
                            remarkPlugins={[remarkMath]}
                            rehypePlugins={[rehypeKatex]}
                        >
                            {hint.text}
                        </Markdown>
                    </div>
                )
            }
            <Button
                variant="ghost"
                className="absolute right-4 bottom-4 opacity-50"
                onClick={() => setPageData({ strokes: [] })}
            >
                Clear
            </Button>
        </div>
    );
};

export default ProblemCanvas;
