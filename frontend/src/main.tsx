import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'

import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";

import MainView from './views/MainView';
import ProblemListView from './views/ProblemListView';
import ProblemView from './views/ProblemView';


const router = createBrowserRouter([
  {
    path: "/",
    element: <MainView />,
  },
  {
    path: "/enter",
    element: <ProblemListView />,
  },
  {
    path: "/problem/:id",
    element: <ProblemView />,
  }
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
