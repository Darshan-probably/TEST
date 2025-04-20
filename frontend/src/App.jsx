import React from 'react';
import InvoiceUploadForm from './components/InvoiceUploadForm';
import InvoiceProcessorVisualization from './components/InvoiceProcessorVisualization';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4">
      <div className="container mx-auto">
        <h1 className="text-3xl font-bold text-center mb-10">Invoice Processor</h1>
        
        <div className="grid md:grid-cols-2 gap-8">
          {/* Left side: Actual working form */}
          <div>
            <InvoiceUploadForm />
          </div>
          
          {/* Right side: Visual representation/demo */}
          <div>
            <h2 className="text-xl font-semibold mb-4">How It Works</h2>
            <InvoiceProcessorVisualization />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
