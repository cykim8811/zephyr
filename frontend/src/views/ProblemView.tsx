import ProblemCanvas from '@/components/ProblemCanvas';
import { ScrollArea } from '@/components/ui/scroll-area';
import React, { useEffect, useRef, useState } from 'react';
import Markdown from 'react-markdown';
import { useParams } from 'react-router-dom';
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';

const problemText = `
삼차함수 $f(x)$가 모든 실수 $x$에 대하여

$xf(x) - f(x) = 3x^4 - 3x$
를 만족시킬 때, $\\int_{-2}^{2} f(x) \\, dx$의 값은?
`;

const ProblemView: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [ pageCount, setPageCount ] = useState(3);

    return (
        <ScrollArea className="w-screen h-screen bg-gray-200 overflow-y-auto">
            <div className="absolute w-full p-4 bg-white opacity-90 z-10 border-b border-gray-200 pointer-events-none">
                <Markdown
                    className="w-fit mx-auto py-4 text-lg"
                    remarkPlugins={[remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                >
                    {problemText}
                </Markdown>
            </div>
            {Array.from({ length: pageCount }).map((_, index) => (
                <ProblemCanvas key={index} />
            ))}
        </ScrollArea>
    );
};

export default ProblemView;