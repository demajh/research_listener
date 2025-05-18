import React, { useState } from 'react';

function App() {
  const [arxivChannel, setArxivChannel] = useState('');
  const [interest, setInterest] = useState('');
  const [email, setEmail] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: POST data to backend /api endpoint
    console.log({ arxivChannel, interest, email });
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Arxiv Listener Dashboard</h1>
      <form onSubmit={handleSubmit}>
        <label>
          arXiv Channel:
          <input
            type="text"
            value={arxivChannel}
            onChange={(e) => setArxivChannel(e.target.value)}
          />
        </label>
        <br /><br />
        <label>
          Area of Interest:
          <input
            type="text"
            value={interest}
            onChange={(e) => setInterest(e.target.value)}
          />
        </label>
        <br /><br />
        <label>
          Email:
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>
        <br /><br />
        <button type="submit">Save Settings</button>
      </form>
    </div>
  );
}

export default App;
