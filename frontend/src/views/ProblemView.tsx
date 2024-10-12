import AIButton from '@/components/AIButton';
import PenToggle from '@/components/PenToggle';
import ProblemCanvas from '@/components/ProblemCanvas';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Hint } from '@/types/hint';
import { PageData } from '@/types/pageData';
import { getCsrfToken } from '@/utils/csrf';
import { addToServer, getFromServer, saveToServer } from '@/utils/sync';
import axios from 'axios';
import { ArrowLeft } from 'lucide-react';
import React, { useEffect, useRef, useState } from 'react';
import Markdown from 'react-markdown';
import { useNavigate, useParams } from 'react-router-dom';
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';

import 'katex/dist/katex.min.css';

function dataURLtoBlob(dataURL: string): Blob {
    const byteString = atob(dataURL.split(',')[1]);
    const mimeString = dataURL.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) ia[i] = byteString.charCodeAt(i);
    return new Blob([ab], { type: mimeString });
}

const ProblemView: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [pageData, setPageData] = useState<PageData[]>([{ strokes: [], }]);
    const [problemText, setProblemText] = useState<string>('');
    const canvasRefs = useRef<HTMLCanvasElement[]>([]);

    const [hint, setHint] = useState<Hint | null>(null);

    useEffect(() => {
        if (id === undefined) return;
        axios.get(`${window.location.origin}/api/problem?id=${id}`)
            .then((response) => {
                setProblemText(response.data.text);
            })
            .catch((e) => {
                alert(e);
            });
        getFromServer(id, setPageData);
    }, [id]);

    const navigate = useNavigate();
    
    const [ penType, setPenType ] = useState<'pen' | 'eraser'>('pen');

    const handleToggle = (e: TouchEvent) => {
        setPenType(penType === 'pen' ? 'eraser' : 'pen');
        e.preventDefault();
    }

    const handleAIClick = async (e: TouchEvent) => {
        if (id === undefined) return;
        const formData = new FormData();
        formData.append('problem_id', id);

        // images : File[]
        
        const images = canvasRefs.current.map((canvas, index) => {
            const dataURL = canvas.toDataURL('image/png');
            const blob = dataURLtoBlob(dataURL);
            return new File([blob], `page_${index}.png`, { type: 'image/png' });
        });

        images.slice(0, images.length - 1).forEach((image) => {
            formData.append('images', image);
        });

        await axios.post(
            window.location.origin + '/api/ai/',
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                    'X-CSRFToken': getCsrfToken(),
                }
            }
        ).then((response) => {
            setHint(response.data);
        }).catch((e) => {
            alert(e);
        });
    }

    return (
        <div className="relative flex flex-col w-screen h-full">
            <ArrowLeft
                size={24}
                className="absolute left-0 top-0 m-4 z-30 mt-8 inline-block mr-2 bg-white"
                onPointerDown={() => navigate('/problem')}
            />
            <div className="w-full p-4 bg-white opacity-95 z-10 border-b border-gray-200 pointer-events-none select-none">
                <Markdown
                    className="w-fit mx-auto text-lg"
                    remarkPlugins={[remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                >
                    {problemText}
                </Markdown>
            </div>
            <ScrollArea
                className="w-screen h-screen bg-gray-200 overflow-y-hidden"
            >
                {Array.from({ length: pageData.length }).map((_, index) => (
                    <ProblemCanvas
                        key={index} penType={penType} pageData={pageData[index]} hint={hint?.page_id === index ? hint : null}
                        setCanvas={(canvas: HTMLCanvasElement) => {
                            canvasRefs.current[index] = canvas;
                        }}
                        setPageData={(data) => {
                            setPageData((pageData) => {
                                pageData[index] = data;
                                let lastFilledIndex = pageData.length - 1;
                                while (lastFilledIndex >= 0 && pageData[lastFilledIndex].strokes.length === 0) lastFilledIndex--;
                                lastFilledIndex += 2;
                                const newPageData = pageData.slice(0, lastFilledIndex);
                                if (id === undefined) return newPageData;
                                saveToServer(newPageData, id);
                                return newPageData;
                            });
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
                <PenToggle className="absolute right-0 top-0 z-20" penType={penType} onClick={handleToggle} />
                <AIButton className="absolute right-0 top-20 z-20" onClick={handleAIClick} />
            </ScrollArea>
        </div>
    );
};

export default ProblemView;