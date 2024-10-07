import { PageData, Stroke } from "@/types/pageData";
import axios from "axios";
import { getCsrfToken } from "./csrf";

export function saveToServer(newPageData: PageData[], id: string) {
    axios.post(
        'https://zephyr.cykim.kr/accounts/solution/',
        {
            problem_id: id,
            texts: JSON.stringify(newPageData),
        },
        {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            }
        }
    ).catch((e) => {
        alert(e);
    });
}

export function addToServer(stroke: Stroke, page_id: number, id: string) {
    axios.post(
        'https://zephyr.cykim.kr/accounts/solution/',
        {
            problem_id: id,
            page_id: page_id,
            stroke: JSON.stringify(stroke),
        },
        {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            }
        }
    ).catch((e) => {
        alert(e);
    });
}

export function getFromServer(id: string, setPageData: (pageData: PageData[]) => void) {
    axios.get(`https://zephyr.cykim.kr/accounts/solution/get?problem_id=${id}`)
        .then((response) => {
            setPageData(JSON.parse(response.data.texts));
        }
        )
        .catch((e) => {
            alert(e);
        });
}