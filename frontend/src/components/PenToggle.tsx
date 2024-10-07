import { Eraser, Pen } from 'lucide-react';
import React, { useEffect, useRef } from 'react';

interface PenToggleProps {
    className?: string;
    penType: 'pen' | 'eraser';
    onClick: (e: TouchEvent) => void;
}



const PenToggle: React.FC<PenToggleProps> = ({ className, penType, onClick }) => {
    const toggleRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        toggleRef.current?.addEventListener('touchstart', onClick, { passive: false });
        return () => {
            toggleRef.current?.removeEventListener('touchstart', onClick);
        };
    }, [onClick]);

    return (
        <div
            ref={toggleRef}
            className={"w-16 h-16 rounded-full border-2 m-4 mt-6 transition-all overflow-hidden"
                + (penType === 'eraser' ? " bg-black border-gray-600" : " bg-white border-gray-100")
                + (className ? ` ${className}` : '')}
        >
            <div
                className="w-[200%] h-full flex justify-center items-center flex-row transition-transform select-none"
                style={{ transform: `translateX(${penType === 'pen' ? 0 : '-50%'})` }}
            >
                <Pen size={26} className="m-4" />
                <Eraser size={26} className="m-4 text-white" />
            </div>
        </div>
    );
};

export default PenToggle;