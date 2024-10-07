import { Button } from '@/components/ui/button';
import React from 'react';

const LoginView: React.FC = () => {
    return (
        <div>
            <Button onClick={() => {window.location.href = "/accounts/google/login";} }>Login with Google</Button>
        </div>
    );
};

export default LoginView;