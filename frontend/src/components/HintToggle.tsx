import { Eraser, Lightbulb, LightbulbOff, Pen } from 'lucide-react';
import React, { useEffect, useRef } from 'react';

interface HintToggleProps {
    className?: string;
    showHint: boolean;
    onClick: (e: TouchEvent) => void;
}



const HintToggle: React.FC<HintToggleProps> = ({ className, showHint, onClick }) => {
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
                + (showHint ? " bg-white border-gray-100" : " bg-black border-gray-600")
                + (className ? ` ${className}` : '')}
        >
            <div
                className="w-[200%] h-full flex justify-center items-center flex-row transition-transform select-none"
                style={{ transform: `translateX(${showHint ? 0 : '-50%'})` }}
            >
                <Lightbulb size={26} className="m-4" />
                <LightbulbOff size={26} className="m-4 text-white" />
            </div>
        </div>
    );
};

export default HintToggle;