import ProblemCanvas from '@/components/ProblemCanvas';
import { ScrollArea } from '@/components/ui/scroll-area';
import React, { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';

const ProblemView: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [ pageCount, setPageCount ] = useState(3);

    return (
        <ScrollArea className="w-screen h-screen bg-gray-200 overflow-y-auto">
            {Array.from({ length: pageCount }).map((_, index) => (
                <ProblemCanvas key={index} />
            ))}
        </ScrollArea>
    );
};

export default ProblemView;