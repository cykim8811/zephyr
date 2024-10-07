import { useProblemCanvasHooks } from '@/hooks/problemCanvasHooks';
import React, { useRef } from 'react';

interface ProblemCanvasProps {
    penType: string;
}

const ProblemCanvas: React.FC<ProblemCanvasProps> = ({ penType }) => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const eraserDisplayRef = useRef<HTMLDivElement>(null);
    useProblemCanvasHooks(canvasRef, eraserDisplayRef, penType);

    return (
        <>
            <canvas
                ref={canvasRef}
                className="w-full bg-white border-t border-b border-gray-200 select-none"
                style={{ aspectRatio: 1 / 1.414 }}
            />
            {
                <div
                    ref={eraserDisplayRef}
                    className="w-[70px] h-[70px] rounded-full border border-gray-300 absolute transform -translate-x-1/2 -translate-y-1/2 pointer-events-none select-none"
                />
            }
        </>
    );
};

export default ProblemCanvas;
