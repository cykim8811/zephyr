import ProblemCanvas from '@/components/ProblemCanvas';
import { ScrollArea } from '@/components/ui/scroll-area';
import { PageData } from '@/types/pageData';
import { ArrowLeft, Eraser, Pen } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import Markdown from 'react-markdown';
import { useNavigate, useParams } from 'react-router-dom';
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';

import { useLocalStorage } from 'usehooks-ts'

const problemText = `
삼차함수 $f(x)$가 모든 실수 $x$에 대하여

$xf(x) - f(x) = 3x^4 - 3x$
를 만족시킬 때, $\\int_{-2}^{2} f(x) \\, dx$의 값은?
`;

const ProblemView: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [pageData, setPageData] = useLocalStorage<PageData[]>(
        `pageData-${id}`,
        [{ strokes: [], }]
    );
    const toggleRef = useRef<HTMLDivElement>(null);
    const navigate = useNavigate();
    
    const [ penType, setPenType ] = useState<'pen' | 'eraser'>('pen');

    const handleTouchStart = (e: TouchEvent) => {
        setPenType(penType === 'pen' ? 'eraser' : 'pen');
        e.preventDefault();
    }

    useEffect(() => {
        toggleRef.current?.addEventListener('touchstart', handleTouchStart, { passive: false });
        return () => {
            toggleRef.current?.removeEventListener('touchstart', handleTouchStart);
        };
    }, [penType]);

    return (
        <ScrollArea
            className="w-screen h-screen bg-gray-200 overflow-y-hidden"
        >
            <ArrowLeft
                size={24}
                className="absolute left-0 top-0 z-20 m-4 mt-8 inline-block mr-2"
                onPointerDown={() => navigate('/enter')}
            />
            <div className="absolute w-full p-4 bg-white opacity-95 z-10 border-b border-gray-200 pointer-events-none select-none">
                <Markdown
                    className="w-fit mx-auto py-4 text-lg"
                    remarkPlugins={[remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                >
                    {problemText}
                </Markdown>
            </div>
            {Array.from({ length: pageData.length }).map((_, index) => (
                <ProblemCanvas key={index} penType={penType} pageData={pageData[index]} setPageData={(data) => {
                    setPageData(pageData.map((d, i) => i === index ? data : d));
                }} />
            ))}
            <div
                ref={toggleRef}
                className={"absolute right-0 top-0 z-20 w-16 h-16 rounded-full border-2 m-4 mt-6 transition-all overflow-hidden"
                    + (penType === 'eraser' ? " bg-black border-gray-600" : " bg-white border-gray-100")}
            >
                <div
                    className="w-[200%] h-full flex justify-center items-center flex-row transition-transform select-none"
                    style={{ transform: `translateX(${penType === 'pen' ? 0 : '-50%'})` }}
                >
                    <Pen size={26} className="m-4" />
                    <Eraser size={26} className="m-4 text-white" />
                </div>
            </div>
        </ScrollArea>
    );
};

export default ProblemView;