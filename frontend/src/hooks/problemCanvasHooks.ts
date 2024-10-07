import React, { useEffect, useRef } from "react";

export function useProblemCanvasHooks(canvasRef: React.RefObject<HTMLCanvasElement>) {
    const lastPointRef = useRef<{ x: number; y: number } | null>(null);

    let isPen = false;
    const handlePointerDown = (e: PointerEvent) => {
        e.preventDefault();
        isPen = e.pointerType === 'pen';
        if (isPen) {
            lastPointRef.current = { x: e.clientX, y: e.clientY - canvasRef.current!.getBoundingClientRect().top };
        } else {
            return;
        }
    };

    const handleTouchStart = (e: TouchEvent) => {
        if (isPen) {
            e.preventDefault();
            e.stopPropagation();
        }
    }

    const handlePointerMove = (e: PointerEvent) => {
        if (e.pointerType === 'pen') {
            const canvas = canvasRef.current;
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            if (!ctx) return;

            if (lastPointRef.current !== null) {
                ctx.beginPath();
                ctx.moveTo(lastPointRef.current.x, lastPointRef.current.y);
                ctx.lineTo(e.clientX, e.clientY - canvas.getBoundingClientRect().top);
                ctx.stroke();
            }

            lastPointRef.current = { x: e.clientX, y: e.clientY - canvas.getBoundingClientRect().top };

            e.preventDefault();
            e.stopPropagation();
        }
    };

    const handlePointerUp = (e: PointerEvent) => {
        if (isPen) {
            lastPointRef.current = null;
            e.preventDefault();
            e.stopPropagation();
        }
    }

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        canvas.width = canvas.clientWidth;
        canvas.height = canvas.clientHeight;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        canvas.addEventListener('pointerdown', handlePointerDown);
        canvas.addEventListener('touchstart', handleTouchStart);
        canvas.addEventListener('pointermove', handlePointerMove);
        canvas.addEventListener('pointerup', handlePointerUp);

        return () => {
            canvas.removeEventListener('pointerdown', handlePointerDown);
            canvas.removeEventListener('touchstart', handleTouchStart);
            canvas.removeEventListener('pointermove', handlePointerMove);
            canvas.removeEventListener('pointerup', handlePointerUp);
        };
    }, []);
}
