import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode"; // ✅ Import jwtDecode
import { useUser } from "../src/utils/UserContext"; // ✅ Import UserContext

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const { setUserId } = useUser(); // ✅ Get setUserId from context

  const handleLogin = async (e) => {
    e.preventDefault();

    const response = await fetch("http://127.0.0.1:8000/api/user/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("token", data.access_token); // ✅ Save token

      // ✅ Decode JWT to get userId and store it
      const decodedToken = jwtDecode(data.access_token);
      setUserId(decodedToken.user_id); // ✅ Store in Context API
      localStorage.setItem("userId", decodedToken.user_id); // Optional: store in localStorage

      navigate("/"); // ✅ Redirect to home page
    } else {
      alert("Login failed: " + data.detail);
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default Login;
