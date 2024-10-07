import PenToggle from '@/components/PenToggle';
import ProblemCanvas from '@/components/ProblemCanvas';
import { ScrollArea } from '@/components/ui/scroll-area';
import { PageData } from '@/types/pageData';
import { addToServer, getFromServer, saveToServer } from '@/utils/sync';
import { ArrowLeft } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import Markdown from 'react-markdown';
import { useNavigate, useParams } from 'react-router-dom';
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';


const problemText = `
삼차함수 $f(x)$가 모든 실수 $x$에 대하여

$xf(x) - f(x) = 3x^4 - 3x$
를 만족시킬 때, $\\int_{-2}^{2} f(x) \\, dx$의 값은?
`;

const ProblemView: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [pageData, setPageData] = useState<PageData[]>([{ strokes: [], }]);

    useEffect(() => { if (id === undefined) return; getFromServer(id, setPageData); }, []);

    const navigate = useNavigate();
    
    const [ penType, setPenType ] = useState<'pen' | 'eraser'>('pen');

    const handleToggle = (e: TouchEvent) => {
        setPenType(penType === 'pen' ? 'eraser' : 'pen');
        e.preventDefault();
    }

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
                    const newPageData = pageData.map((d, i) => i === index ? data : d);
                    if (newPageData.length >= 2
                        && newPageData[newPageData.length - 1].strokes.length === 0
                        && newPageData[newPageData.length - 2].strokes.length === 0) {
                        newPageData.pop();
                    }
                    if (id === undefined) return;
                    saveToServer(newPageData, id);
                    setPageData(newPageData);
                }}
                addPageData={(stroke) => {
                    setPageData((pageData) => {
                        if (id === undefined) return pageData;

                        if (pageData[pageData.length - 1].strokes.length !== 0) {
                            pageData[index].strokes.push(stroke);
                            pageData.push({ strokes: [] });
                            saveToServer(pageData, id);
                            return pageData;
                        } else {
                            addToServer(stroke, index, id);
                            return pageData.map((d, i) => i === index ? { strokes: [...d.strokes, stroke] } : d)
                        }
                    });
                }}
                />
            ))}
            <PenToggle penType={penType} onClick={handleToggle} />
        </ScrollArea>
    );
};

export default ProblemView;