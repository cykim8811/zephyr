import { SparklesIcon } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';

interface AIButtonProps {
    className?: string;
    onClick: (e: TouchEvent) => void;
}



const AIButton: React.FC<AIButtonProps> = ({ className, onClick }) => {
    const toggleRef = useRef<HTMLDivElement>(null);
    const [isProcessing, setIsProcessing] = useState(false);

    function customOnClick(e: TouchEvent) {
        e.preventDefault();
        (async () => {
            setIsProcessing(true);
            await onClick(e);
            setIsProcessing(false);
        })();
    }

    useEffect(() => {
        toggleRef.current?.addEventListener('touchstart', customOnClick, { passive: false });
        return () => {
            toggleRef.current?.removeEventListener('touchstart', customOnClick);
        };
    }, [customOnClick]);

    return (
        <div
            ref={toggleRef}
            className={"w-16 h-16 rounded-full border-2 m-4 mt-6 transition-all overflow-hidden"
                + (isProcessing ? " bg-gray-400 border-gray-400 text-gray-200" : " bg-white border-gray-100 text-gray-800")
                + (className ? ` ${className}` : '')}
        >
            {/* <SparklesIcon size={26} className="m-4" /> */}
            <div className="w-full h-full flex flex-col justify-center text-lg text-center">
                제출
            </div>
        </div>
    );
};

export default AIButton;