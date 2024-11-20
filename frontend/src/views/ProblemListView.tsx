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
    { id: 3, name: "방정식 1", difficulty: "Hard", chapter: "실험 10/28" },
    { id: 4, name: "방정식 2", difficulty: "Hard", chapter: "실험 10/28" },
    { id: 5, name: "방정식 3", difficulty: "Hard", chapter: "실험 10/28" },
    { id: 6, name: "방정식 4-1", difficulty: "Hard", chapter: "실험 10/28" },
    { id: 7, name: "방정식 4-2", difficulty: "Hard", chapter: "실험 10/28" },
    { id: 8, name: "방정식 5", difficulty: "Hard", chapter: "실험 10/28" },
    { id: 9, name: "수능 1번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    { id: 10, name: "수능 2번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    { id: 11, name: "수능 3번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    { id: 12, name: "수능 4번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 13, name: "수능 5번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 14, name: "수능 6번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 15, name: "수능 7번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 16, name: "수능 8번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 17, name: "수능 9번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 18, name: "수능 10번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    { id: 19, name: "수능 11번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    { id: 20, name: "수능 12번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    { id: 21, name: "수능 13번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    { id: 22, name: "수능 14번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    { id: 23, name: "수능 15번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 24, name: "수능 16번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 25, name: "수능 17번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 26, name: "수능 18번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 27, name: "수능 19번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 28, name: "수능 20번", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 39, name: "수능 21번 (미적분)", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 40, name: "수능 22번 (미적분)", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 41, name: "수능 23번 (미적분)", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 42, name: "수능 24번 (미적분)", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 43, name: "수능 25번 (미적분)", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 44, name: "수능 26번 (미적분)", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 45, name: "수능 27번 (미적분)", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    // { id: 46, name: "수능 28번 (미적분)", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    { id: 47, name: "수능 29번 (미적분)", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" },
    { id: 48, name: "수능 30번 (미적분)", difficulty: "Hard", chapter: "2024년도 대학수학능력시험 수학영역" }
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