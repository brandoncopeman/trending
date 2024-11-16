import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TrendList.css';

const TrendList = () => {
  const [trends, setTrends] = useState([]);
  const [search, setSearch] = useState('');

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/trends')
      .then(response => setTrends(response.data))
      .catch(error => {
        console.error("Error fetching data:", error);
        setTrends([{ title: "Mock Post 1" }, { title: "Mock Post 2" }]);
      });
  }, []);

  const filteredTrends = trends.filter(trend =>
    trend.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="TrendList">
      <h1>Trending Posts</h1>
      <input
        type="text"
        placeholder="Search trends..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <ul>
        {filteredTrends.map((trend, index) => (
          <li key={index}>{trend.title}</li>
        ))}
      </ul>
    </div>
  );
};

export default TrendList;
