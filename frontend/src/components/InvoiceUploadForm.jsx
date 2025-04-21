import { useState } from 'react';
import { FileUp, Upload, Download, Settings, Loader } from 'lucide-react';

export default function InvoiceUploadForm() {
  const [file, setFile] = useState(null);
  const [bags, setBags] = useState('');
  const [weight, setWeight] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [minPercent, setMinPercent] = useState('-2');
  const [maxPercent, setMaxPercent] = useState('2');
  const [preserveWrapping, setPreserveWrapping] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  
  // New fields
  const [templateType, setTemplateType] = useState('default');
  const [date, setDate] = useState('');
  const [address, setAddress] = useState('');
  const [lotNumber, setLotNumber] = useState('');
  const [name, setName] = useState('');

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.toLowerCase().endsWith('.xlsx')) {
      setFile(selectedFile);
      setErrorMessage('');
    } else {
      setFile(null);
      setErrorMessage('Please select a valid Excel (.xlsx) file');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setErrorMessage('Please select a file to process');
      return;
    }

    setIsProcessing(true);
    setDownloadUrl('');
    setErrorMessage('');

    const formData = new FormData();
    formData.append('file', file);
    if (bags) formData.append('bags', bags);
    if (weight) formData.append('weight', weight);
    // Default font size is set to 9 in the backend
    formData.append('font_size', '9');
    formData.append('min_percent', minPercent);
    formData.append('max_percent', maxPercent);
    formData.append('preserve_wrapping', preserveWrapping.toString());
    
    // Append new fields if they have values
    if (templateType !== 'default') formData.append('template_type', templateType);
    if (date) formData.append('date', date);
    if (address) formData.append('address', address);
    if (lotNumber) formData.append('lot_number', lotNumber);
    if (name) formData.append('name', name);

    try {
      const response = await fetch('/process/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error processing file');
      }

      const data = await response.json();
      setDownloadUrl(data.download_url);
    } catch (error) {
      setErrorMessage(error.message || 'Error processing the invoice');
      console.error('Processing error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h1 className="text-2xl font-bold text-center mb-6">Invoice Processor</h1>
      
      {errorMessage && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4">
          <p>{errorMessage}</p>
        </div>
      )}
      
      {downloadUrl ? (
        <div className="text-center p-6 bg-green-50 rounded-lg mb-6">
          <Download size={48} className="text-green-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-4">Processing Complete!</h2>
          <p className="mb-4">Your invoice has been processed successfully.</p>
          <a 
            href={downloadUrl} 
            className="bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600 inline-flex items-center"
          >
            <Download size={16} className="mr-2" />
            Download Processed File
          </a>
          <button 
            onClick={() => {
              setFile(null);
              setDownloadUrl('');
            }}
            className="block mx-auto mt-4 text-green-600 hover:underline"
          >
            Process another file
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Template Selection */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-medium mb-4">Template Selection</h3>
            <div className="grid grid-cols-1 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Select Template Type
                </label>
                <select
                  value={templateType}
                  onChange={(e) => setTemplateType(e.target.value)}
                  className="w-full p-2 border rounded"
                >
                  <option value="default">Default Template</option>
                  <option value="invoice1">Invoice Template 1</option>
                  <option value="invoice2">Invoice Template 2</option>
                  <option value="custom">Custom Template</option>
                </select>
              </div>
            </div>
          </div>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input
              type="file"
              id="fileInput"
              onChange={handleFileChange}
              className="hidden"
              accept=".xlsx"
            />
            <label 
              htmlFor="fileInput" 
              className="cursor-pointer flex flex-col items-center"
            >
              <FileUp size={48} className="text-blue-500 mb-4" />
              <span className="text-lg font-medium mb-2">
                {file ? file.name : 'Click to select Excel file'}
              </span>
              <span className="text-sm text-gray-500">
                {file ? `Size: ${(file.size / 1024).toFixed(2)} KB` : 'Only .xlsx files accepted'}
              </span>
            </label>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-medium mb-4 flex items-center">
              <Settings size={18} className="mr-2" />
              Processing Options
            </h3>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Number of Bags
                </label>
                <input
                  type="number"
                  value={bags}
                  onChange={(e) => setBags(e.target.value)}
                  className="w-full p-2 border rounded"
                  placeholder="Auto-detect"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Total Weight (kg)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={weight}
                  onChange={(e) => setWeight(e.target.value)}
                  className="w-full p-2 border rounded"
                  placeholder="Auto-detect"
                />
              </div>
            </div>
            
            {/* Document Information */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Document Information (Optional)</h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">
                    Date
                  </label>
                  <input
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    className="w-full p-2 border rounded"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-600 mb-1">
                    Lot Number
                  </label>
                  <input
                    type="text"
                    value={lotNumber}
                    onChange={(e) => setLotNumber(e.target.value)}
                    className="w-full p-2 border rounded"
                    placeholder="Enter lot number"
                  />
                </div>
              </div>
              
              <div className="mt-3">
                <label className="block text-xs text-gray-600 mb-1">
                  Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full p-2 border rounded"
                  placeholder="Enter name"
                />
              </div>
              
              <div className="mt-3">
                <label className="block text-xs text-gray-600 mb-1">
                  Address
                </label>
                <textarea
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  className="w-full p-2 border rounded"
                  placeholder="Enter address"
                  rows="2"
                />
              </div>
            </div>
            
            <div className="mb-4">
              <button 
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="text-blue-500 text-sm font-medium flex items-center"
              >
                {showAdvanced ? 'Hide' : 'Show'} Advanced Options
                <span className={`ml-1 transition-transform ${showAdvanced ? 'rotate-180' : ''}`}>▼</span>
              </button>
            </div>
            
            {showAdvanced && (
              <div className="bg-white p-4 rounded border border-gray-200 mb-4 space-y-4">                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Min Variation %
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      value={minPercent}
                      onChange={(e) => setMinPercent(e.target.value)}
                      className="w-full p-2 border rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Max Variation %
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      value={maxPercent}
                      onChange={(e) => setMaxPercent(e.target.value)}
                      className="w-full p-2 border rounded"
                    />
                  </div>
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="preserveWrapping"
                    checked={preserveWrapping}
                    onChange={(e) => setPreserveWrapping(e.target.checked)}
                    className="mr-2"
                  />
                  <label htmlFor="preserveWrapping" className="text-sm text-gray-700">
                    Preserve text wrapping
                  </label>
                </div>
              </div>
            )}
          </div>
          
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={!file || isProcessing}
              className={`bg-blue-500 text-white px-6 py-2 rounded flex items-center ${
                (!file || isProcessing) ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-600'
              }`}
            >
              {isProcessing ? (
                <>
                  <Loader size={16} className="mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Upload size={16} className="mr-2" />
                  Process Invoice
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}