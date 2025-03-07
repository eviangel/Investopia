import { createContext, useContext, useState, useEffect } from "react";

// Create context
const UserContext = createContext();

// Provider component
export const UserProvider = ({ children }) => {
  // 1) Initialize userId from localStorage
  const [userId, setUserId] = useState(() => {
    return localStorage.getItem("userId") || null;
  });

  // 2) Keep localStorage in sync with userId changes
  useEffect(() => {
    if (userId) {
      localStorage.setItem("userId", userId);
    } else {
      localStorage.removeItem("userId");
    }
  }, [userId]);

  return (
    <UserContext.Provider value={{ userId, setUserId }}>
      {children}
    </UserContext.Provider>
  );
};

// Custom hook for easy access
export const useUser = () => useContext(UserContext);
