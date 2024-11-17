import React from 'react';

const TrendItem = ({ idea, count, url }) => {
  return (
    <li>
      <strong>{idea}</strong> ({" "}{count} )
      <br />
      <a href={url} target="_blank" >
        View Post
      </a>
    </li>
  );
};

export default TrendItem;