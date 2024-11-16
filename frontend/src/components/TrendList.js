import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TrendItem from './TrendItem';
import './TrendList.css';

const TrendList = () => {
  const [trends, setTrends] = useState([]);

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/trends')
      .then(response => {
        console.log("Data fetched:", response.data); // Log the data
        setTrends(response.data);
      })
      .catch(error => {
        console.error("Error fetching data:", error);
        // Fallback mock data
        setTrends([
          { idea: "Mock Idea 1", count: 10, url: "https://example.com/1" },
          { idea: "Mock Idea 2", count: 5, url: "https://example.com/2" }
        ]);
      });
  }, []);

  return (
    <div>
      <h1>Trending Posts</h1>
      <ul>
        {trends.map((trend, index) => (
          <TrendItem 
            key={index} 
            idea={trend.idea} 
            count={trend.count} 
          
          />
        ))}
      </ul>
    </div>
  );
};

export default TrendList;
