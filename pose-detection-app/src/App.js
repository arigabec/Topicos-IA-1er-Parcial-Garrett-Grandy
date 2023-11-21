import React, { useState } from 'react';
import ApiButtons from './components/ApiButtons';

function App() {
  const [apiResponse, setApiResponse] = useState(null);

  return (
    <div className="App">
      <ApiButtons setApiResponse={setApiResponse} />
    </div>
  );
}

export default App;
