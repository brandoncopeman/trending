import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TrendList.css';

const TrendList = () => {
  const [trends, setTrends] = useState([]);
  const [expandedIdea, setExpandedIdea] = useState(null); // Tracks which idea is expanded

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/trends')
      .then(response => {
        setTrends(response.data);
      })
      .catch(error => {
        console.error("Error fetching data:", error);
      });
  }, []);

  const toggleExpand = (idea) => {
    setExpandedIdea(expandedIdea === idea ? null : idea);
  };

  return (
    <div className="TrendList">
      <h1>Trending Posts</h1>
      <ul>
        {trends.map((trend, index) => (
          <li key={index}>
            <div onClick={() => toggleExpand(trend.idea)} className="idea-name">
              <strong>{trend.idea}</strong> — {trend.count} 
            </div>
            {expandedIdea === trend.idea && (
              <ul className="titles-list">
                {trend.titles.map((item, idx) => (
                  <li key={idx}>
                    <a href={item.url} target="_blank" rel="noopener noreferrer">
                      {item.title}
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TrendList;
