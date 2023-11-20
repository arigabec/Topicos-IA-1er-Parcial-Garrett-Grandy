import React from 'react';

const ApiResponse = ({ apiResponse }) => {
  return (
    <div>
      <h2> API Response </h2>
      <pre>{JSON.stringify(apiResponse, null, 12)}</pre>

    </div>
    
  );
};

export default ApiResponse;
