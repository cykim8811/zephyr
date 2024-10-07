import React, { useEffect, useRef } from "react";


const dpr = window.devicePixelRatio || 1;

export function useProblemCanvasHooks(canvasRef: React.RefObject<HTMLCanvasElement>) {
    const lastPointRef = useRef<{ x: number; y: number }[]>([]);

    let isPen = false;
    const handlePointerDown = (e: PointerEvent) => {
        e.preventDefault();
        isPen = e.pointerType === 'pen';
        if (isPen) {
            lastPointRef.current = [{ x: e.clientX, y: e.clientY - canvasRef.current!.getBoundingClientRect().top }];
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

            const dist = Math.hypot(e.clientX - lastPointRef.current[lastPointRef.current.length - 1].x, e.clientY - canvas.getBoundingClientRect().top - lastPointRef.current[lastPointRef.current.length - 1].y);
            if (dist < 2) return;

            lastPointRef.current.push({ x: e.clientX, y: e.clientY - canvas.getBoundingClientRect().top });

            ctx.lineWidth = 3;
            ctx.lineCap = 'round';
            ctx.strokeStyle = 'black';
            ctx.beginPath();
            ctx.moveTo(lastPointRef.current[lastPointRef.current.length - 2].x * dpr, lastPointRef.current[lastPointRef.current.length - 2].y * dpr);
            ctx.lineTo(lastPointRef.current[lastPointRef.current.length - 1].x * dpr, lastPointRef.current[lastPointRef.current.length - 1].y * dpr);
            ctx.stroke();


            e.preventDefault();
            e.stopPropagation();
        }
    };

    const handlePointerUp = (e: PointerEvent) => {
        if (isPen) {
            lastPointRef.current = [];
            e.preventDefault();
            e.stopPropagation();
        }
    }

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        canvas.width = canvas.clientWidth * dpr;
        canvas.height = canvas.clientHeight * dpr;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = 'high';

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
