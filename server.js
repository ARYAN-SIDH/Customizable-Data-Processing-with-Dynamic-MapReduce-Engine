// server.js
const express = require('express');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');

const app = express();
const port = 3001;

app.use(bodyParser.json());

app.post('/api/submit-job', async (req, res) => {
  const jobConfig = req.body;
  try {
    // Execute MapReduce job
    const result = await executeMapReduceJob(jobConfig);
    res.json({ result });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'An error occurred while processing the job.' });
  }
});

async function executeMapReduceJob(jobConfig) {
  // Generate MapReduce job command based on job configuration
  const { inputDataSource, mapFunction, reduceFunction, outputDestination } = jobConfig;
  const command = `hadoop jar <path_to_jar_file> <map_reduce_class> ${inputDataSource} ${outputDestination}`;

  // Execute MapReduce job
  return new Promise((resolve, reject) => {
    const jobProcess = spawn('bash', ['-c', command]);
    let output = '';

    jobProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    jobProcess.stderr.on('data', (data) => {
      console.error(`stderr: ${data}`);
    });

    jobProcess.on('close', (code) => {
      if (code === 0) {
        resolve(output);
      } else {
        reject(new Error(`MapReduce job failed with exit code ${code}`));
      }
    });
  });
}

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
