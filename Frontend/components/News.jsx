import React from 'react';
import './News.css';

const News = () => {
  return (
    <div className="news">
      <h3 className="news-title">News</h3>
      <ul className="news-list">
        <li>What will happen to bitcoin in the coming week</li>
        <li>US Treasury to introduce tax rules for cryptocurrency</li>
      </ul>
    </div>
  );
};

export default News;