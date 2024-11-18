import React from 'react';

const TrendItem = ({ idea, count, titles }) => {
  return (
    <li>
      <strong>{idea}</strong> ({count} occurrences)
      <ul>
        {titles.map((item, idx) => (
          <li key={idx}>
            <a href={item.url} target="_blank" rel="noopener noreferrer">
              {item.title} — <em>{item.source}</em>
            </a>
          </li>
        ))}
      </ul>
    </li>
  );
};

export default TrendItem;
