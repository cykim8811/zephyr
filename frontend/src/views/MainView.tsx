import { Input } from "@/components/ui/input";
import SnuIcon from "@/assets/snu.png";
import { Button } from "@/components/ui/button";
import { ArrowRightIcon } from "lucide-react";

import React from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { getCsrfToken } from "@/utils/csrf";
import { Base64 } from "js-base64";

const MainView: React.FC = () => {
    const navigate = useNavigate();
    const [name, setName] = React.useState("");
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
                <div>
                    <Input placeholder="이름" className="text-xl" value={name} onChange={(e) => setName(e.target.value)} />
                    <Button className="w-full mt-4 text-xl"
                        onClick={async () => {
                            const base64name = Base64.encode(name);
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
                                        "X-CSRFToken": getCsrfToken(),
                                    },
                                }
                            );
                            
                            await axios.post(
                                `/accounts/login/`,
                                {
                                    email: `${base64name}@cykim.kr`,
                                    password: "asfDASd689789dsf##@asdf",
                                },
                                {
                                    headers: {
                                        'Content-Type': 'application/x-www-form-urlencoded',
                                        "X-CSRFToken": getCsrfToken(),
                                    },
                                }
                            );

                            navigate("/problem");
                        }}>
                        학생 로그인<ArrowRightIcon size={16} className="mr-2" />
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default MainView;