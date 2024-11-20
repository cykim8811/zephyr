import { PageData, Stroke } from "@/types/pageData";
import React, { useEffect, useRef } from "react";


const dpr = window.devicePixelRatio || 1;

const penWidth = 1.8;
const dotDistance = 0.1;

function drawStroke(ctx: CanvasRenderingContext2D, original_stroke: Stroke) {
    const stroke = {
        type: original_stroke.type,
        points: original_stroke.points.map(p => ({ x: p.x, y: p.y }))
    };

    for (let i = 1; i < stroke.points.length - 1; i++) {
        const p0 = stroke.points[i - 1];
        const p1 = stroke.points[i];
        const p2 = stroke.points[i + 1];

        const m = { x: (p0.x + p2.x) / 2, y: (p0.y + p2.y) / 2 };
        const dx = (p1.x - m.x) * 0.5;
        const dy = (p1.y - m.y) * 0.5;

        stroke.points[i] = { x: p1.x - dx, y: p1.y - dy };
    }

    ctx.lineWidth = stroke.type === 'pen' ? penWidth * dpr : 60 * dpr;
    ctx.strokeStyle = stroke.type === 'pen' ? 'black' : 'white';

    if (stroke.points.length < 2) return;

    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    ctx.beginPath();

    // 첫 점으로 이동
    ctx.moveTo(stroke.points[0].x * dpr, stroke.points[0].y * dpr);

    // 베지어 곡선을 사용한 스플라인 보간
    for (let i = 1; i < stroke.points.length - 2; i++) {
        const xc = (stroke.points[i].x + stroke.points[i + 1].x) / 2 * dpr;
        const yc = (stroke.points[i].y + stroke.points[i + 1].y) / 2 * dpr;
        ctx.quadraticCurveTo(
            stroke.points[i].x * dpr,
            stroke.points[i].y * dpr,
            xc, yc
        );
    }

    // 마지막 두 점을 처리
    if (stroke.points.length > 2) {
        ctx.quadraticCurveTo(
            stroke.points[stroke.points.length - 2].x * dpr,
            stroke.points[stroke.points.length - 2].y * dpr,
            stroke.points[stroke.points.length - 1].x * dpr,
            stroke.points[stroke.points.length - 1].y * dpr
        );
    }

    ctx.stroke();
}

export function useProblemCanvasHooks(
    canvasRef: React.RefObject<HTMLCanvasElement>,
    eraserDisplayRef: React.RefObject<HTMLDivElement>,
    penType: "pen" | "eraser",
    pageData: PageData,
    setPageData: (pageData: PageData) => void,
    addPageData: (stroke: Stroke) => void,
    overlayCanvasRef: React.RefObject<HTMLCanvasElement>) {

    const pageDataRef = useRef(pageData);

    const lastPointRef = useRef<{ x: number; y: number }[]>([]);
    const penTypeRef = useRef(penType);

    const ctxRef = useRef<CanvasRenderingContext2D | null>(null);
    const overlayCtxRef = useRef<CanvasRenderingContext2D | null>(null);

    useEffect(() => {
        if (canvasRef.current) {
            ctxRef.current = canvasRef.current.getContext('2d');
        }
        if (overlayCanvasRef.current) {
            overlayCtxRef.current = overlayCanvasRef.current.getContext('2d');
        }
    }, []);

    useEffect(() => {
        penTypeRef.current = penType;
    }, [penType]);

    useEffect(() => {
        pageDataRef.current = pageData;
        redrawCanvas();
    }, [pageData]);

    let isPen = false;
    const handlePointerDown = (e: PointerEvent) => {
        isPen = e.pointerType === 'pen';
        if (isPen) {
            lastPointRef.current = [{ x: e.clientX, y: e.clientY - canvasRef.current!.getBoundingClientRect().top }];
            // if (penTypeRef.current === 'eraser') {
            //     eraserDisplayRef.current!.style.display = 'block';
            //     eraserDisplayRef.current!.style.left = e.clientX + 'px';
            //     eraserDisplayRef.current!.style.top = e.clientY - canvasRef.current!.getBoundingClientRect().top + 'px';
            // }
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
            const ctx = ctxRef.current;
            if (!ctx) return;

            if (penTypeRef.current === 'eraser') {
                // eraserDisplayRef.current!.style.left = e.clientX + 'px';
                // eraserDisplayRef.current!.style.top = e.clientY - canvas.getBoundingClientRect().top + 'px';

                // Remove strokes collided with eraser
                const currentPoint = { x: e.clientX, y: e.clientY - canvas.getBoundingClientRect().top };
                const eraserSize = 10 * dpr;

                let isDifferent = false;
                const newStrokes = pageDataRef.current.strokes.map(stroke => {
                    if (stroke.type === 'pen') {
                        for (let i = 0; i < stroke.points.length - 1; i++) {
                            const p0 = stroke.points[i];
                            const p1 = stroke.points[i + 1];
                            const dx = p1.x - p0.x;
                            const dy = p1.y - p0.y;
                            const dist = Math.hypot(
                                (currentPoint.x - p0.x) * dy - (currentPoint.y - p0.y) * dx,
                                (currentPoint.x - p0.x) * dx + (currentPoint.y - p0.y) * dy
                            ) / Math.hypot(dx, dy);
                            if (dist < eraserSize && stroke.erasedTimestamp === undefined) {
                                isDifferent = true;
                                return { ...stroke, erasedTimestamp: Date.now() };
                            }
                        }
                    }
                    return stroke;
                });

                if (isDifferent) {
                    setPageData({ strokes: newStrokes });
                    redrawCanvas();
                }

                return;
            }

            if (!overlayCtxRef.current) return;

            overlayCtxRef.current?.clearRect(0, 0, canvas.width, canvas.height);

            const currentPoint = { x: e.clientX, y: e.clientY - canvas.getBoundingClientRect().top };

            const dist = Math.hypot(currentPoint.x - lastPointRef.current.slice(-1)[0].x, currentPoint.y - lastPointRef.current.slice(-1)[0].y);

            lastPointRef.current.push(currentPoint);

            const stroke = {
                type: penTypeRef.current,
                points: lastPointRef.current.map(p => ({ x: p.x, y: p.y })),
                timestamp: Date.now()
            };

            drawStroke(overlayCtxRef.current, stroke);

            if (dist < dotDistance * dpr) {
                lastPointRef.current.pop();
            }

            e.preventDefault();
            e.stopPropagation();
        }
    };

    const handlePointerUp = (e: PointerEvent) => {
        if (isPen) {
            // Check if canvas is all white
            const canvas = canvasRef.current;
            if (!canvas) return;
            const ctx = ctxRef.current;
            if (!ctx) return;

            lastPointRef.current.push({ x: e.clientX, y: e.clientY - canvas.getBoundingClientRect().top });

            drawStroke(ctx, {
                type: penTypeRef.current,
                points: lastPointRef.current.map(p => ({ x: p.x, y: p.y })),
                timestamp: Date.now()
            });

            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
            let isWhite = true;
            for (let i = 0; i < imageData.length; i += 4) {
                if (imageData[i] !== 255 || imageData[i + 1] !== 255 || imageData[i + 2] !== 255 || imageData[i + 3] !== 255) {
                    isWhite = false;
                    break;
                }
            }

            if (isWhite) {
                setPageData({ strokes: [] });
            } else {
                addPageData({
                    type: penTypeRef.current,
                    points: lastPointRef.current.map(p => ({ x: p.x, y: p.y })),
                    timestamp: Date.now()
                });
            }
            lastPointRef.current = [];
            e.preventDefault();
            e.stopPropagation();

            eraserDisplayRef.current!.style.display = 'none';
        }
    };

    function redrawCanvas() {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = ctxRef.current;
        if (!ctx) return;

        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        pageData.strokes.forEach(stroke => {
            if (stroke.erasedTimestamp) return;
            drawStroke(ctx, stroke);
        });
    }

    useEffect(() => {
        const canvas = canvasRef.current;
        const overlayCanvas = overlayCanvasRef.current;
        if (!canvas) return;
        if (!overlayCanvas) return;
        canvas.width = canvas.clientWidth * dpr;
        canvas.height = canvas.clientHeight * dpr;
        overlayCanvas.width = overlayCanvas.clientWidth * dpr;
        overlayCanvas.height = overlayCanvas.clientHeight * dpr;

        const ctx = ctxRef.current;
        if (!ctx) return;

        ctx.translate(0.5, 0.5);
        overlayCtxRef.current?.translate(0.5, 0.5);

        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        redrawCanvas();

        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = 'high';

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
