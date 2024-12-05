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
    showHint: boolean;
    streamingNum: number;
}

const ProblemCanvas: React.FC<ProblemCanvasProps> = ({ penType, pageData, setPageData, addPageData, setCanvas, hint, showHint, streamingNum }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
    const eraserDisplayRef = useRef<HTMLDivElement>(null);
    const hintRef = useRef<HTMLDivElement>(null);
    useProblemCanvasHooks(canvasRef, eraserDisplayRef, penType, pageData, setPageData, addPageData, overlayCanvasRef);

    const [checkWrite, setCheckWrite] = useState<boolean>(false);

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
            setCheckWrite(false);
            while (true) {
                let done = false;
                setHintText((prev) => {
                    if (prev.length >= hint.text.length) {
                        done = true;
                    }
                    return hint.text.slice(0, prev.length + 1);
                });
                if (done) break;
                await new Promise((resolve) => setTimeout(resolve, 30));
            }
        })();
    }, [hint]);
    
    let dollarCount = 0;
    for (let i = 0; i < hintText.length; i++) {
        if (hintText[i] === '$') dollarCount++;
    }

    let boxColor = 'border-gray-500';

    if (hint?.text == "*N") boxColor = 'border-gray-500';
    else if (hint?.text == "*G") boxColor = 'border-green-500';
    else if (hint?.text.startsWith("*P")) boxColor = 'border-purple-500';
    else boxColor = 'border-red-500';

    const hintTextAtBottom = (hint?.top??0) * window.innerWidth * 1.414 < ((hintRef.current?.offsetHeight ?? 0) * 1.5 + 40);
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
                    <span className={
                        showHint ? 'opacity-100' : 'opacity-0'
                    }>
                        <motion.div
                            key={`${streamingNum}-box`}
                            className="absolute pointer-events-none select-none overflow-hidden"
                            initial={{
                                left: window.innerWidth * Math.max(hint.left - 0.05, 0) - window.innerWidth * 0.1,
                                top: window.innerWidth * 1.414 * Math.max(hint.top - 0.05, 0) - window.innerWidth * 0.1,
                                width: window.innerWidth * (Math.min((hint.right - hint.left) + 0.1 + Math.max(hint.left - 0.05, 0), 1) - Math.max(hint.left - 0.05, 0)) + window.innerWidth * 0.2,
                                height: window.innerWidth * 1.414 * (Math.min((hint.bottom - hint.top + 0.1 + Math.max(hint.top - 0.05, 0)), 1) - Math.max(hint.top - 0.05, 0)) + window.innerWidth * 0.2,
                                opacity: 0.0,
                            }}
                            animate={{
                                left: window.innerWidth * Math.max(hint.left - 0.05, 0),
                                top: window.innerWidth * 1.414 * Math.max(hint.top - 0.05, 0),
                                width: window.innerWidth * (Math.min((hint.right - hint.left) + 0.1 + Math.max(hint.left - 0.05, 0), 1) - Math.max(hint.left - 0.05, 0)),
                                height: window.innerWidth * 1.414 * (Math.min((hint.bottom - hint.top + 0.1 + Math.max(hint.top - 0.05, 0)), 1) - Math.max(hint.top - 0.05, 0)),
                                opacity: 1,
                            }}
                            
                            transition={{
                                duration: 0.4,
                                ease: 'easeInOut',
                            }}
                        >
                            <div className="w-full h-full flex flex-row justify-between p-4">
                                <div className="h-full flex flex-col justify-between">
                                    <div className={`w-4 h-4 transition-colors border-l-4 border-t-4 rounded-tl-md ${boxColor}`} />
                                    <div className={`w-4 h-4 transition-colors border-l-4 border-b-4 rounded-bl-md ${boxColor}`} />
                                </div>
                                <div className="h-full flex flex-col justify-between">
                                    <div className={`w-4 h-4 transition-colors border-r-4 border-t-4 rounded-tr-md ${boxColor}`} />
                                    <div className={`w-4 h-4 transition-colors border-r-4 border-b-4 rounded-br-md ${boxColor}`} />
                                </div>
                            </div>
                        </motion.div>
                        { hintText.length > 2 &&
                            <motion.div
                                key={`${streamingNum}-text`}
                                ref={hintRef}
                                className="absolute p-8 text-black text-xl word-wrap select-none break-keep border-2 border-gray-500/80 bg-white/95 rounded-xl opacity-70 shadow-xl"
                                style={{
                                    transform: hintTextAtBottom ?
                                        `translate(-50%, 120px)` :
                                        `translate(-50%, ${-(hintRef.current?.offsetHeight ?? 0) - 80}px)`,
                                    transition: 'transform 0.5s',
                                    maxWidth: '80%',
                                    width: 'fit-content',
                                    left: '50vw',
                                    top: hintTextAtBottom ? (hint.bottom * window.innerWidth * 1.414 * 1.1) : (hint.top * window.innerWidth * 1.414),
                                }}
                                initial={{
                                    opacity: 0.0,
                                }}
                                animate={{
                                    opacity: 1,
                                }}
                                transition={{
                                    duration: 0.3,
                                    delay: 0.7,
                                }}
                            >
                                {
                                    checkWrite ?
                                    <Markdown
                                        remarkPlugins={[remarkMath]}
                                        rehypePlugins={[rehypeKatex]}
                                    >
                                        {hintText.replace('*P', '') + ((dollarCount % 2 == 1)?'$': '')}
                                    </Markdown>
                                    :
                                    <>
                                    <Markdown
                                        remarkPlugins={[remarkMath]}
                                        rehypePlugins={[rehypeKatex]}
                                    >
                                        {`"${hint.user_input}" 이라고 작성하신 게 맞나요?`}
                                    </Markdown>
                                    <div className="w-full flex flex-row justify-evenly">
                                        <Button
                                            onClick={() => setCheckWrite(true)}
                                            className="mt-4 w-16"
                                        >
                                            네
                                        </Button>
                                        <Button
                                            onClick={() => {
                                                setCheckWrite(true);
                                                setHintText('정확한 인식을 위해, 풀이를 정자로 작성해주세요.');
                                            }}
                                            className="mt-4 w-16"
                                        >
                                            아니요
                                        </Button>
                                    </div>
                                    </>
                                }
                            </motion.div>
                        }
                    </span>
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
