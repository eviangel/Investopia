const API_URL = "http://127.0.0.1:8000/api";

export const fetchProtectedData = async () => {
  const token = localStorage.getItem("token");

  const response = await fetch(`${API_URL}/user/protected`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "Authorization": token, // ✅ Include token in headers
    },
  });

  if (!response.ok) {
    throw new Error("Unauthorized: Token invalid or expired.");
  }

  return response.json();
};
