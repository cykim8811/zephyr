import { useProblemCanvasHooks } from '@/hooks/problemCanvasHooks';
import { Hint } from '@/types/hint';
import { PageData, Stroke } from '@/types/pageData';
import React, { useRef } from 'react';

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
            {
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
            }
        </div>
    );
};

export default ProblemCanvas;
