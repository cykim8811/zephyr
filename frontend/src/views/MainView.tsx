import { Input } from "@/components/ui/input";
import SnuIcon from "@/assets/snu.png";
import { Button } from "@/components/ui/button";
import { ArrowRightIcon } from "lucide-react";

import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { getCsrfToken } from "@/utils/csrf";
import { Base64 } from "js-base64";

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.withCredentials = true;

const MainView: React.FC = () => {
    const navigate = useNavigate();
    const [name, setName] = React.useState("");

    useEffect(() => {
        (async () => {
            const response = await axios.get(
                `/accounts/info/`,
                {
                    withCredentials: true,
                }
            );
            if (response.data.username) {
                console.log(response.data.username);
            }
        })();
    }, []);
    
    const handlePress = () => {
        (async () => {
            let base64name = Base64.encode(name);
            base64name = base64name.toLowerCase();
            try {
                await axios.post(
                    `/accounts/signup/`,
                    {
                        username: name,
                        email: `${base64name}@cykim.kr`,
                        password1: "asfDASd689789dsf##@asdf",
                        password2: "asfDASd689789dsf##@asdf",
                    },
                    {
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                    }
                );
            } catch (e) {
                
            }
            const res = await axios.post(
                `/accounts/login2/`,
                {
                    email: `${base64name}@cykim.kr`,
                    password: "asfDASd689789dsf##@asdf",
                },
                {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCsrfToken(),
                    },
                }
            );
            document.body.innerHTML = res.data;
            navigate("/problem");
        })();
    }
    return (
        <div className="w-screen h-screen bg-white flex flex-col justify-center items-center">
            <div className="w-fit flex flex-col">
                <div className="text-center text-xl flex flex-row justify-start items-center mb-8">
                    <img src={SnuIcon} alt="SNU" className="w-9 h-9" />
                    <div className="text-xs text-left ml-4">
                        서울대학교 수학교육과<br />
                        공동연구지원사업 AI 커스터마이징
                    </div>
                </div>
                <div className="mb-40">
                    <Input placeholder="이름" className="text-xl" value={name} onChange={(e) => setName(e.target.value)} />
                    <Button className="w-full mt-4 text-xl"
                        onClick={handlePress}
                        onTouchEnd={handlePress}
                    >
                        학생 로그인<ArrowRightIcon size={16} className="mr-2" />
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default MainView;