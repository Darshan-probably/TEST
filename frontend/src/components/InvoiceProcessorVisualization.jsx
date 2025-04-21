import { useState } from 'react';
import { FileUp, ArrowRight, Download, Settings, RefreshCw } from 'lucide-react';

export default function InvoiceProcessorVisualization() {
  const [step, setStep] = useState(1);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [previewActive, setPreviewActive] = useState(false);
  
  const nextStep = () => {
    if (step < 4) setStep(step + 1);
    else setStep(1);
  };
  
  const prevStep = () => {
    if (step > 1) setStep(step - 1);
  };
  
  return (
    <div className="flex flex-col w-full bg-gray-50 p-4 rounded-lg">
      <h2 className="text-xl font-bold mb-6 text-center">Invoice Processor System Visualization</h2>
      
      {/* Progress indicator */}
      <div className="flex justify-between mb-6 px-2">
        {[1, 2, 3, 4].map(num => (
          <div key={num} className="flex flex-col items-center">
            <div 
              className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step >= num ? 'bg-blue-500 text-white' : 'bg-gray-200'
              }`}
            >
              {num}
            </div>
            <span className={`text-xs mt-1 ${step >= num ? 'text-blue-500' : 'text-gray-500'}`}>
              {num === 1 ? 'Upload' : num === 2 ? 'Configure' : num === 3 ? 'Process' : 'Download'}
            </span>
          </div>
        ))}
      </div>
      
      {/* Flow visualization */}
      <div className="border rounded-lg bg-white p-6 mb-4 min-h-64">
        {step === 1 && (
          <div className="flex flex-col items-center">
            <div className="bg-blue-100 p-8 rounded-lg flex flex-col items-center mb-6">
              <FileUp size={48} className="text-blue-500 mb-4" />
              <h3 className="text-lg font-semibold">Upload Invoice Excel File</h3>
              <p className="text-gray-600 text-center mt-2">User uploads an Excel invoice file via the web interface</p>
            </div>
            <div className="bg-blue-50 p-4 rounded border border-blue-200 w-full max-w-md">
              <h4 className="font-medium text-blue-700 mb-2">System Actions</h4>
              <ul className="text-sm text-blue-800 list-disc pl-5 space-y-1">
                <li>Receives uploaded Excel file</li>
                <li>Validates file format and extension</li>
                <li>Assigns unique ID for processing</li>
                <li>Stores file temporarily for processing</li>
              </ul>
            </div>
          </div>
        )}
        
        {step === 2 && (
          <div className="flex flex-col items-center">
            <div className="bg-blue-100 p-6 rounded-lg flex flex-col items-center mb-6 w-full max-w-md">
              <Settings size={40} className="text-blue-500 mb-4" />
              <h3 className="text-lg font-semibold">Configure Processing Options</h3>
              <div className="mt-4 w-full">
                <div className="flex flex-col gap-2">
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Template Type:</span>
                    <span className="text-sm text-gray-600">Default</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Number of Bags:</span>
                    <span className="text-sm text-gray-600">25</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Total Weight (kg):</span>
                    <span className="text-sm text-gray-600">1000.50</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Date:</span>
                    <span className="text-sm text-gray-600">2025-04-21</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm font-medium">Lot Number:</span>
                    <span className="text-sm text-gray-600">LN-123456</span>
                  </div>
                  <button 
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="text-blue-500 text-sm font-medium mt-2 flex items-center"
                  >
                    {showAdvanced ? 'Hide' : 'Show'} Advanced Options
                    <span className={`ml-1 transition-transform ${showAdvanced ? 'rotate-180' : ''}`}>▼</span>
                  </button>
                  
                  {showAdvanced && (
                    <div className="bg-gray-50 p-3 rounded border border-gray-200 mt-2">
                      <div className="flex justify-between text-xs mt-2">
                        <span>Min Variation: <b>-2%</b></span>
                        <span>Max Variation: <b>2%</b></span>
                      </div>
                      <div className="flex items-center text-xs mt-2">
                        <input type="checkbox" checked className="mr-2" readOnly />
                        <span>Preserve text wrapping</span>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="flex gap-2 mt-4">
                  <button className={`flex-1 p-2 text-white rounded text-sm flex items-center justify-center ${previewActive ? 'bg-green-600' : 'bg-blue-500'}`} onClick={() => setPreviewActive(!previewActive)}>
                    {previewActive ? 'Preview Active' : 'Preview Changes'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {step === 3 && (
          <div className="flex flex-col items-center">
            <div className="bg-blue-100 p-6 rounded-lg flex flex-col items-center mb-6">
              <RefreshCw size={40} className="text-blue-500 mb-4" />
              <h3 className="text-lg font-semibold">Invoice Processing</h3>
              <p className="text-gray-600 text-center mt-2">The system processes the Excel file</p>
            </div>
            
            <div className="bg-blue-50 p-4 rounded border border-blue-200 w-full max-w-md">
              <h4 className="font-medium text-blue-700 mb-2">Processing Steps</h4>
              <ol className="text-sm text-blue-800 list-decimal pl-5 space-y-2">
                <li>Load Excel workbook</li>
                <li>Determine the number of bags (from input or detect)</li>
                <li>Insert additional rows if needed</li>
                <li>Calculate weight distribution with variation</li>
                <li>Apply updated values and formatting</li>
                <li>Add document information (date, lot number, etc.)</li>
                <li>Save as new Excel file</li>
              </ol>
            </div>
          </div>
        )}
        
        {step === 4 && (
          <div className="flex flex-col items-center">
            <div className="bg-green-100 p-8 rounded-lg flex flex-col items-center mb-6">
              <Download size={48} className="text-green-500 mb-4" />
              <h3 className="text-lg font-semibold">Download Processed Invoice</h3>
              <p className="text-gray-600 text-center mt-2">User downloads the processed Excel file with redistributed weights</p>
            </div>
            
            <div className="border border-gray-300 rounded p-4 bg-gray-50 w-full max-w-md">
              <h4 className="font-semibold mb-2">Result Preview</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full text-xs">
                  <thead className="bg-gray-200">
                    <tr>
                      <th className="p-2 border">Item</th>
                      <th className="p-2 border">Description</th>
                      <th className="p-2 border">Weight</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="bg-white">
                      <td className="p-2 border">Bag 1</td>
                      <td className="p-2 border">Coffee Beans A</td>
                      <td className="p-2 border text-right">40.15 kg</td>
                    </tr>
                    <tr className="bg-gray-50">
                      <td className="p-2 border">Bag 2</td>
                      <td className="p-2 border">Coffee Beans A</td>
                      <td className="p-2 border text-right">39.87 kg</td>
                    </tr>
                    <tr className="bg-white">
                      <td className="p-2 border">Bag 3</td>
                      <td className="p-2 border">Coffee Beans A</td>
                      <td className="p-2 border text-right">40.32 kg</td>
                    </tr>
                    <tr className="bg-gray-200 font-semibold">
                      <td className="p-2 border" colSpan="2">Total</td>
                      <td className="p-2 border text-right">120.34 kg</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Navigation buttons */}
      <div className="flex justify-between mt-4">
        <button 
          onClick={prevStep} 
          className={`px-4 py-2 rounded ${step > 1 ? 'bg-gray-200 hover:bg-gray-300' : 'bg-gray-100 text-gray-400 cursor-not-allowed'}`}
          disabled={step <= 1}
        >
          Previous
        </button>
        <button 
          onClick={nextStep} 
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 flex items-center"
        >
          {step === 4 ? 'Restart' : 'Next'} 
          <ArrowRight size={16} className="ml-1" />
        </button>
      </div>
    </div>
  );
}