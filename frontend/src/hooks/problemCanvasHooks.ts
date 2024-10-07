import { p } from "framer-motion/client";
import React, { useEffect, useRef } from "react";


const dpr = window.devicePixelRatio || 1;

export function useProblemCanvasHooks(canvasRef: React.RefObject<HTMLCanvasElement>, eraserDisplayRef: React.RefObject<HTMLDivElement>, penType: string) {
    const lastPointRef = useRef<{ x: number; y: number }[]>([]);
    const penTypeRef = useRef(penType);

    useEffect(() => {
        penTypeRef.current = penType;
    }, [penType]);

    let isPen = false;
    const handlePointerDown = (e: PointerEvent) => {
        isPen = e.pointerType === 'pen';
        if (isPen) {
            lastPointRef.current = [{ x: e.clientX, y: e.clientY - canvasRef.current!.getBoundingClientRect().top }];
            if (penTypeRef.current === 'eraser') {
                eraserDisplayRef.current!.style.display = 'block';
                eraserDisplayRef.current!.style.left = e.clientX + 'px';
                eraserDisplayRef.current!.style.top = e.clientY + 'px';
            }
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

            if (penTypeRef.current === 'eraser') {
                eraserDisplayRef.current!.style.left = e.clientX + 'px';
                eraserDisplayRef.current!.style.top = e.clientY + 'px';
            }

            const dist = Math.hypot(e.clientX - lastPointRef.current[lastPointRef.current.length - 1].x, e.clientY - canvas.getBoundingClientRect().top - lastPointRef.current[lastPointRef.current.length - 1].y);
            if (dist < 2) return;

            lastPointRef.current.push({ x: e.clientX, y: e.clientY - canvas.getBoundingClientRect().top });

            ctx.lineWidth = penTypeRef.current === 'pen' ? 2 * dpr : 70 * dpr;
            ctx.lineCap = 'round';

            if (penTypeRef.current === 'pen') {
                ctx.strokeStyle = 'black';
                ctx.globalCompositeOperation = 'source-over';
            } else {
                ctx.strokeStyle = 'white';
                ctx.globalCompositeOperation = 'destination-out';
            }

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

            eraserDisplayRef.current!.style.display = 'none';
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

        canvas.addEventListener('pointerdown', handlePointerDown, { passive: true, capture: true });
        canvas.addEventListener('touchstart', handleTouchStart, { passive: false, capture: false });
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
