// components/JobConfigForm.js
import React, { useState } from 'react';

function JobConfigForm() {
  const [config, setConfig] = useState({
    inputDataSource: '',
    mapFunction: '',
    reduceFunction: '',
    outputDestination: '',
    // Add more job parameters here
  });

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      const response = await fetch('/api/submit-job', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
      });
      const data = await response.json();
      console.log(data);
      // Handle response from backend
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setConfig({ ...config, [name]: value });
  };

  return (
    <form onSubmit={handleSubmit}>
      <label>
        Input Data Source:
        <input type="text" name="inputDataSource" value={config.inputDataSource} onChange={handleChange} />
      </label>
      <label>
        Map Function:
        <textarea name="mapFunction" value={config.mapFunction} onChange={handleChange} />
      </label>
      <label>
        Reduce Function:
        <textarea name="reduceFunction" value={config.reduceFunction} onChange={handleChange} />
      </label>
      <label>
        Output Destination:
        <input type="text" name="outputDestination" value={config.outputDestination} onChange={handleChange} />
      </label>
      {/* Add more input fields for other job parameters */}
      <button type="submit">Submit Job</button>
    </form>
  );
}

export default JobConfigForm;
