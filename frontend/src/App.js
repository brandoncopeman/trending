import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
    const [trends, setTrends] = useState([]);

    useEffect(() => {
        axios.get('http://127.0.0.1:5000/trends')
            .then((response) => {
                setTrends(response.data);
            })
            .catch((error) => console.error(error));
    }, []);

    return (
        <div>
            <h1>Trending Topics</h1>
            <ul>
                {trends.map((trend, index) => (
                    <li key={index}>{trend.title}</li>
                ))}
            </ul>
        </div>
    );
}

export default App;
