import React from 'react';
import './TopBar.css';
import { useNavigate } from 'react-router-dom';

const TopBar = () => {
  const navigate = useNavigate();

  const handleSignIn = () => {
    console.log('Sign In button clicked');
    navigate('/signin'); // Adjust the path based on your routing structure
  };

  const handleAbout = () => {
    navigate('/about'); // Adjust the path based on your routing structure
  };

  const handleDocs = () => {
    navigate('/docs'); // Adjust the path based on your routing structure
  };

  return (
    <div className="top-bar">
      <div className="top-bar-left">
      </div>
      <div className="top-bar-right">
        <button className="top-bar-button" onClick={handleDocs}>Docs</button>
        <button className="top-bar-button" onClick={handleAbout}>About</button>
        <button className="top-bar-button sign-in" onClick={handleSignIn}>Sign In</button>
      </div>
    </div>
  );
};

export default TopBar;



