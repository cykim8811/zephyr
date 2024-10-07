import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

type Problem = {
  id: number;
  name: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  chapter: string;
};

const problems: Problem[] = [
    { id: 1, name: "문제 1", difficulty: "Easy", chapter: "1장" },
    { id: 2, name: "문제 2", difficulty: "Medium", chapter: "2장" },
    { id: 3, name: "문제 3", difficulty: "Hard", chapter: "3장" },
];

const ProblemListView: React.FC = () => {
  const navigate = useNavigate();
  const [nextPageTransition, setNextPageTransition] = useState(false);

  return (
    <motion.div
      className="container mx-auto p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: nextPageTransition ? 0 : 1 }}
      transition={{ duration: 0.36, ease: "easeIn" }}
    >
      <h1 className="text-2xl md:text-3xl font-bold text-gray-800 mb-4 w-full text-center mt-8 mb-[6rem]" style={{fontFamily: "Noto Serif"}}>Problems</h1>
      <ScrollArea className="h-[70vh]">
        <div className="space-y-4 flex flex-col">
          {problems.map((problem) => (
            <Button
              key={problem.id}
              variant="outline"
              className="w-full"
              onClick={() => {
                setNextPageTransition(true);
                setTimeout(() => {
                  navigate(`/problem/${problem.id}`);
                }, 360);
              }}
            >
              <div className="w-full p-2 flex flex-row justify-between items-center text-lg">
                  <div className="flex flex-row items-center">
                      {problem.name}
                  </div>
                  <div className="flex flex-row items-center">
                      <span className="text-sm text-gray-500 w-16 flex justify-end">{problem.chapter}</span>
                </div>
              </div>
            </Button>
          ))}
        </div>
      </ScrollArea>
    </motion.div>
  );
};

export default ProblemListView;