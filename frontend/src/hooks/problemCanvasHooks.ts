import React, { useEffect } from "react";

export function useProblemCanvasHooks(canvasRef: React.RefObject<HTMLCanvasElement>) {
    let isPen = false;
    const handlePointerDown = (e: PointerEvent) => {
        e.preventDefault();
        isPen = e.pointerType === 'pen';
        if (e.pointerType === 'pen') {
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

            ctx.fillStyle = 'black';
            ctx.beginPath();
            ctx.arc(e.clientX, e.clientY - canvas.getBoundingClientRect().top, 1, 0, 2 * Math.PI);
            ctx.fill();

            e.preventDefault();
            e.stopPropagation();
        }
    };

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

        return () => {
            canvas.removeEventListener('pointerdown', handlePointerDown);
            canvas.removeEventListener('touchstart', handleTouchStart);
            canvas.removeEventListener('pointermove', handlePointerMove);
        };
    }, []);
}
