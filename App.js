// App.js
import React, { useState } from 'react';
import JobConfigForm from './components/JobConfigForm';

function App() {
  return (
    <div className="App">
      <h1>Dynamic Job Configuration</h1>
      <JobConfigForm />
    </div>
  );
}

export default App;
