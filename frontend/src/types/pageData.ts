
export interface Stroke {
    type: 'pen' | 'eraser';
    points: { x: number; y: number }[];
    timestamp: number;
}

export interface PageData {
    strokes: Stroke[];
}
