import React, { useState } from 'react';
import ApiButtons from './components/ApiButtons';
import ApiResponse from './components/ApiResponse';

function App() {
  const [apiResponse, setApiResponse] = useState(null);

  return (
    <div className="App">
      <ApiButtons setApiResponse={setApiResponse} />
      <ApiResponse apiResponse={apiResponse} />
    </div>
  );
}

export default App;
