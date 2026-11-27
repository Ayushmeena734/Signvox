const API_BASE_URL = "http://127.0.0.1:8000";

export async function testBackend() {
  const response = await fetch(`${API_BASE_URL}/test`);

  if (!response.ok) {
    throw new Error("Backend connection failed");
  }

  return response.json();
}

export async function predictSign(landmarks) {
  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ landmarks }),
  });

  if (!response.ok) {
    throw new Error("Prediction request failed");
  }

  return response.json();
}