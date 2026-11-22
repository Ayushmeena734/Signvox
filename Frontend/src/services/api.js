
const API_BASE_URL = "http://127.0.0.1:8000";

export async function testBackend() {
    const response = await fetch(`${API_BASE_URL}/test`);

    if (!response.ok) {
        throw new Error("Backend connection failed");
    }

    return response.json();
}
