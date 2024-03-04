// Node.js server code
const express = require('express');
const { exec } = require('child_process');
const fetch = require('node-fetch');

const app = express();
const PORT = process.env.PORT || 3000;

// Serve static files (HTML, CSS, JS)
app.use(express.static('public'));

// Route to execute Python code
app.get('/execute', async (req, res) => {
  try {
    // Fetch Python file from GitHub repository
    const response = await fetch('https://raw.githubusercontent.com/your_username/your_repository/master/your_python_file.py');
    const pythonCode = await response.text();

    // Execute Python code
    exec(`python -c "${pythonCode}"`, (error, stdout, stderr) => {
      if (error) {
        res.status(500).send(error.message);
        return;
      }
      if (stderr) {
        res.status(500).send(stderr);
        return;
      }
      res.send(stdout);
    });
  } catch (err) {
    console.error(err);
    res.status(500).send('Internal Server Error');
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
