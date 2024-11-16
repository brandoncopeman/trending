import React from 'react';
import TrendList from './components/TrendList';
import './App.css';


function App() {
  return (
    <div className="App-container">
      {/* Left sidebar (hidden for now) */}
      <div className="App-sidebar">
        <p>Left Sidebar</p>
      </div>

      {/* Main content */}
      <div className="App-main">
        <TrendList />
      </div>

      {/* Right sidebar (hidden for now) */}
      <div className="App-sidebar-right">
        <p>Right Sidebar</p>
      </div>
    </div>
  );
}

export default App;
