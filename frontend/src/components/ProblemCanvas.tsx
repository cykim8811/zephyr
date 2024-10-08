import { useProblemCanvasHooks } from '@/hooks/problemCanvasHooks';
import { Hint } from '@/types/hint';
import { PageData, Stroke } from '@/types/pageData';
import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import Markdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

interface ProblemCanvasProps {
    penType: 'pen' | 'eraser';
    pageData: PageData;
    setPageData: (pageData: PageData) => void;
    addPageData: (stroke: Stroke) => void;
    hint: Hint | null;
}

const ProblemCanvas: React.FC<ProblemCanvasProps> = ({ penType, pageData, setPageData, addPageData, hint }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const eraserDisplayRef = useRef<HTMLDivElement>(null);
    useProblemCanvasHooks(canvasRef, eraserDisplayRef, penType, pageData, setPageData, addPageData);

    const [hintText, setHintText] = useState<string>('');

    useEffect(() => {
        setHintText('');
        (async () => {
            if (hint === null) return;
            while (hintText.length < hint.text.length) {
                let done = false;
                setHintText((prev) => {
                    if (prev.length === hint.text.length) {
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
            {
                <div
                    ref={eraserDisplayRef}
                    className="w-[60px] h-[60px] rounded-full border border-gray-300 absolute transform -translate-x-1/2 -translate-y-1/2 pointer-events-none select-none"
                />
            }
            {/* {
                hint && (
                    <div
                        className="absolute p-2 border border-red-300"
                        style={{
                            left: window.innerWidth * hint.left,
                            top: window.innerWidth * 1.5 * hint.top,
                            width: window.innerWidth * (hint.right - hint.left),
                            height: window.innerWidth * 1.5 * (hint.bottom - hint.top),
                        }}
                    >
                        {hint.text}
                    </div>
                )
            } */}
            {
                hint && (
                    <>
                        <motion.div
                            key={`${hint.left}-${hint.right}-${hint.top}-${hint.bottom}`}
                            className="absolute text-transparent decoration-red-600 pointer-events-none select-none overflow-hidden underline decoration-wavy"
                            style={{
                                left: window.innerWidth * hint.left,
                                top: window.innerWidth * 1.5 * hint.bottom - 46,
                                overflow: 'hidden',
                                fontSize: '48px',
                            }}
                            initial={{ width: 0 }}
                            animate={{ width: window.innerWidth * (hint.right - hint.left) }}
                            transition={{ duration: 0.5, ease: 'linear' }}
                        >
                            {"aaaaaaaaa".repeat(Math.round((hint.right - hint.left) * 10))}
                        </motion.div>
                        <div
                            key={`${hint.left}-${hint.right}-${hint.top}-${hint.bottom}-text`}
                            className="absolute p-2 text-red-700 text-3xl word-wrap pointer-events-none select-none break-keep"
                            style={{
                                fontFamily: 'Nanum Pen Script, cursive',
                                left: window.innerWidth * hint.left,
                                top: window.innerWidth * 1.5 * hint.bottom + 10,
                                width: window.innerWidth - window.innerWidth * hint.left,
                            }}
                        >
                            <Markdown
                                remarkPlugins={[remarkMath]}
                                rehypePlugins={[rehypeKatex]}
                            >
                                {hintText}
                            </Markdown>
                        </div>
                    </>
                )
            }
        </div>
    );
};

export default ProblemCanvas;
