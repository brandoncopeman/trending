import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TrendItem from './TrendItem';


const TrendList = () => {
  const [trends, setTrends] = useState([]);

  useEffect(() => {
    // Replace with actual API endpoint when ready
    axios.get('http://127.0.0.1:5000/trends') // Use http://127.0.0.1:5000/trends for testing with Flask
      .then(response => {
        setTrends(response.data);
      })
      .catch(error => {
        console.error("Error fetching data:", error);
        // Fallback to mock data for now
        setTrends([{ title: "Mock Post 1" }, { title: "Mock Post 2" }]);
      });
  }, []);

  return (
    <div>
      <h1>Trending Posts</h1>
      <ul>
        {trends.map((trend, index) => (
          <TrendItem key={index} title={trend.title} />
        ))}
      </ul>
    </div>
  );
};

export default TrendList;
