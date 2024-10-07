
export function getCsrfToken() {
    const name = 'csrftoken';
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        const part = parts.pop();
        if (part) {
            const subParts = part.split(';');
            if (subParts.length > 0) {
                return subParts.shift();
            }
        }
    }
}