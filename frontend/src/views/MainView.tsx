import React, { useEffect, useState } from 'react';
import Markdown from 'react-markdown'
import { motion } from 'framer-motion';

import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

import "katex/dist/katex.min.css";
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';

const MainView: React.FC = () => {
    const [tutortext, setTutortext] = useState("tuter.");
    useEffect(() => {
        setTimeout(() => {setTutortext("tuter");}, 5000);
        setTimeout(() => {setTutortext("tute");}, 5100);
        setTimeout(() => {setTutortext("tut");}, 5200);
        setTimeout(() => {setTutortext("tuto");}, 5300);
        setTimeout(() => {setTutortext("tutor");}, 5400);
        setTimeout(() => {setTutortext("tutor.");}, 5500);
    }, []);
    return (
        <div className="flex justify-center items-center h-screen text-7xl flex-col" style={{ fontFamily: "Noto Serif"}}>
            <motion.span 
                className="flex flex-row items-center italic"
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
            >
                <Markdown
                remarkPlugins={[remarkMath]}
                rehypePlugins={[rehypeKatex]}
                >
                $Z$
                </Markdown>
                <span style={{fontSize: "1.05em", marginBottom: "0.4rem"}}>ephyr.</span>
            </motion.span>
            <motion.div 
                className="text-2xl mt-20 mb-8"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
            >
                Your personal real-time AI math <span className="text-transparent">tuter.</span>
                <div className="absolute right-0 top-0 text-2xl text-black">
                <div className="absolute">{tutortext}</div>
                    <motion.div
                        className="relative"
                        initial={{ opacity: 1 }}
                        animate={{ opacity: 0 }}
                        transition={{ duration: 0.2, delay: 5.8 }}
                    >
                        <motion.div
                            className="decoration-wavy underline decoration-red-600 overflow-hidden text-transparent"
                            initial={{ width: 0 }}
                            animate={{ width: "100%" }}
                            transition={{ duration: 0.5, delay: 2.3 }}
                        >
                            tutor.
                        </motion.div>
                        <motion.div
                            className="absolute top-8 -left-14 text-red-600 text-xl overflow-hidden fit-content"
                            style={{ fontFamily: "Kalam" }}
                            initial={{ maxWidth: 0 }}
                            animate={{ maxWidth: "400%" }}
                            transition={{ duration: 1.2, delay: 2.8 }}
                        >
                            <div className="whitespace-nowrap max-content block">
                                Check the spelling of 'tuter'.
                            </div>
                        </motion.div>
                        <span className="text-transparent">tutor.</span>
                    </motion.div>
                </div>
            </motion.div>
            <motion.div
                className="text-xl mb-12"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.8, delay: 1, ease: "easeOut" }}
            >
                <Button>
                    Get Started
                    <ArrowRight size={16} />
                </Button>
            </motion.div>
        </div>
    );
};

export default MainView;