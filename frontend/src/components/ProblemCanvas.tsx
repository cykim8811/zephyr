import { useProblemCanvasHooks } from '@/hooks/problemCanvasHooks';
import React, { useRef } from 'react';

const ProblemCanvas: React.FC = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    useProblemCanvasHooks(canvasRef);
    return (
        <canvas
            ref={canvasRef}
            className="w-full bg-white border-t border-b border-gray-200 select-none"
            style={{ aspectRatio: 1 / 1.414 }}
        />
    );
};

export default ProblemCanvas;
