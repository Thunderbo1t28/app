import React, { useState, useEffect } from 'react';
import LoadData from './LoadData';

function App() {
  const [instruments, setInstruments] = useState([]);

  useEffect(() => {
    fetch('/api/instruments')
      .then(res => res.json())
      .then(data => setInstruments(data));
  }, []);

  return (
    <div>
      <LoadData instruments={instruments} />
    </div>
  );
}

export default App; 