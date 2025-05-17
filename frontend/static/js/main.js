document.addEventListener('DOMContentLoaded', function() {
    // Tab Navigation
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Show active content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${tabId}-tab`) {
                    content.classList.add('active');
                }
            });
            
            // If PDF Preview tab is selected, fetch PDFs
            if (tabId === 'preview') {
                fetchPdfs();
            }
        });
    });
    
    // File Upload Handling
    const fileInput = document.getElementById('file-input');
    const uploadArea = document.getElementById('upload-area');
    const fileInfo = document.getElementById('file-info');
    const previewButton = document.getElementById('preview-button');
    const processButton = document.getElementById('process-button');
    
    if (uploadArea) {
        uploadArea.addEventListener('click', function() {
            fileInput.click();
        });
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const file = this.files[0];
            
            if (file) {
                if (file.name.toLowerCase().endsWith('.xlsx')) {
                    fileInfo.textContent = `Selected file: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
                    fileInfo.classList.remove('hidden');
                    previewButton.disabled = false;
                    processButton.disabled = false;
                    hideError();
                } else {
                    showError('Please select a valid Excel (.xlsx) file');
                    fileInfo.classList.add('hidden');
                    previewButton.disabled = true;
                    processButton.disabled = true;
                }
            } else {
                fileInfo.classList.add('hidden');
                previewButton.disabled = true;
                processButton.disabled = true;
            }
        });
    }
    
    // Advanced Options Toggle
    const toggleAdvanced = document.getElementById('toggle-advanced');
    const advancedOptions = document.getElementById('advanced-options');
    const toggleIcon = document.getElementById('toggle-icon');
    
    if (toggleAdvanced) {
        toggleAdvanced.addEventListener('click', function() {
            if (advancedOptions.style.display === 'block') {
                advancedOptions.style.display = 'none';
                toggleAdvanced.textContent = 'Show Advanced Options ';
                toggleIcon.textContent = '▼';
            } else {
                advancedOptions.style.display = 'block';
                toggleAdvanced.textContent = 'Hide Advanced Options ';
                toggleIcon.textContent = '▲';
            }
        });
    }
    
    // Form Submission for Processing
    const uploadForm = document.getElementById('upload-form');
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');
    const outputPath = document.getElementById('output-path');
    const downloadLink = document.getElementById('download-link');
    const processAnother = document.getElementById('process-another');
    const processIcon = document.getElementById('process-icon');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!fileInput.files[0]) {
                showError('Please select a file to process');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            // Add form fields to formData
            const fields = [
                'template_type', 'bags', 'weight', 'date', 'lot_number', 
                'name', 'address', 'min_percent', 'max_percent'
            ];
            
            fields.forEach(field => {
                const element = document.getElementById(field.replace('_', '-'));
                if (element && element.value) {
                    formData.append(field, element.value);
                }
            });
            
            // Add checkbox value
            const preserveWrapping = document.getElementById('preserve-wrapping');
            formData.append('preserve_wrapping', preserveWrapping.checked.toString());
            
            // Show processing state
            processButton.disabled = true;
            processIcon.textContent = '⏳';
            processButton.textContent = ' Processing...';
            hideError();
            
            try {
                const response = await fetch('/api/process/', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Error processing file');
                }
                
                const data = await response.json();
                
                // Show success message
                uploadForm.classList.add('hidden');
                successMessage.classList.remove('hidden');
                
                if (data.file_path) {
                    outputPath.innerHTML = `<div style="background-color: #f8f9fa; padding: 10px; border-radius: 4px; display: inline-block;">
                        <strong>Output Location:</strong> ${data.file_path}
                    </div>`;
                }
                
                // Set download link
                downloadLink.href = data.download_url;
                
                // Add a View PDF button
                const filename = data.download_url.split('/').pop();
                const viewPdfBtn = document.createElement('a');
                viewPdfBtn.href = `/file-preview?filename=${encodeURIComponent(filename)}`;
                viewPdfBtn.className = 'btn';
                viewPdfBtn.innerHTML = 'View PDF';
                viewPdfBtn.style.marginLeft = '10px';
                downloadLink.parentNode.appendChild(viewPdfBtn);
                
                // Trigger PDF updated event for preview tab
                const pdfUpdatedEvent = new CustomEvent('pdfUpdated', {
                    detail: { pdfUrl: data.download_url }
                });
                window.dispatchEvent(pdfUpdatedEvent);
                
            } catch (error) {
                showError(error.message || 'Error processing the invoice');
                console.error('Processing error:', error);
                
                // Reset processing state
                processButton.disabled = false;
                processIcon.textContent = '📤';
                processButton.textContent = ' Process Invoice';
            }
        });
    }
    
    // Process Another Button
    if (processAnother) {
        processAnother.addEventListener('click', function() {
            successMessage.classList.add('hidden');
            uploadForm.classList.remove('hidden');
            fileInput.value = '';
            fileInfo.classList.add('hidden');
            previewButton.disabled = true;
            processButton.disabled = true;
            processIcon.textContent = '📤';
            processButton.textContent = ' Process Invoice';
        });
    }
    
    // Preview Button
    if (previewButton) {
        previewButton.addEventListener('click', async function() {
            if (!fileInput.files[0]) {
                showError('Please select a file to preview');
                return;
            }
            
            // Show previewing state
            previewButton.disabled = true;
            let previewIcon = document.getElementById('preview-icon');
            previewIcon.textContent = '⏳';
            previewButton.textContent = ' Previewing...';
            hideError();
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            // Add form fields to formData (same as process)
            const fields = [
                'template_type', 'bags', 'weight', 'date', 'lot_number', 
                'name', 'address', 'min_percent', 'max_percent'
            ];
            
            fields.forEach(field => {
                const element = document.getElementById(field.replace('_', '-'));
                if (element && element.value) {
                    formData.append(field, element.value);
                }
            });
            
            const preserveWrapping = document.getElementById('preserve-wrapping');
            formData.append('preserve_wrapping', preserveWrapping.checked.toString());
            
            try {
                const response = await fetch('/api/preview/', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || 'Error previewing file');
                }
                
                const data = await response.json();
                
                // Debug logging
                console.log("Preview API response:", data);
                
                // Pull PDF URL from fileInfo if it's not at root level
                // This handles both old and new API response formats
                const pdfPreviewUrl = data.pdfPreviewUrl || (data.fileInfo && `/api/download/${data.fileInfo.pdfFile}`);
                const pdfFilename = data.pdfFilename || (data.fileInfo && data.fileInfo.pdfFile);
                
                console.log("PDF Preview URL:", pdfPreviewUrl);
                console.log("PDF Filename:", pdfFilename);
                
                const previewSection = document.getElementById('preview-section');
                const previewData = document.getElementById('preview-data');
                
                // Check if we have a PDF preview URL
                if (pdfPreviewUrl || pdfFilename) {
                    // Use the determined PDF filename
                    console.log("Using PDF filename for preview:", pdfFilename);
                    
                    // Create JSON string from metadata
                    const metadataJSON = JSON.stringify(data.metadata || {});
                    
                    // Check if we have the PDF filename
                    if (!pdfFilename) {
                        console.error("No PDF filename available for preview");
                        showError("Unable to generate PDF preview - no filename provided");
                        return;
                    }
                    
                    console.log("Using PDF filename for preview:", pdfFilename);
                    
                    // Create the preview URL with proper encoding - MUST USE file-preview route
                    const previewUrl = `/file-preview?filename=${encodeURIComponent(pdfFilename)}&metadata=${encodeURIComponent(metadataJSON)}`;
                    console.log("Generated preview URL:", previewUrl);
                    
                    // Save the PDF URL for direct download if needed
                    if (pdfPreviewUrl) {
                        sessionStorage.setItem('pdfDirectUrl', pdfPreviewUrl);
                    }
                    
                    // Debug information 
                    console.log("Current page:", window.location.href);
                    console.log("PDF filename:", pdfFilename);
                    
                    // Show preview information in the current page first
                    const previewSection = document.getElementById('preview-section');
                    const previewData = document.getElementById('preview-data');
                    
                    previewData.innerHTML = `
                        <div class="success-message" style="margin-bottom: 20px;">
                            <h3>PDF Preview Ready</h3>
                            <p>Your PDF has been successfully generated.</p>
                            <div style="display: flex; gap: 10px; justify-content: center; margin-top: 20px;">
                                <a href="${previewUrl}" target="_blank" class="btn btn-success">Open PDF Preview</a>
                                <a href="/api/download/${encodeURIComponent(pdfFilename)}" download class="btn">Download PDF</a>
                            </div>
                        </div>
                    `;
                    previewSection.classList.remove('hidden');
                    
                    // Check user preference for opening preview 
                    // Default to opening in a new tab, but can be configured
                    const openInNewTab = localStorage.getItem('openPreviewInNewTab') !== 'false'; // Default to true
                    
                    try {
                        if (openInNewTab) {
                            const newWindow = window.open(previewUrl, '_blank');
                            console.log("Preview window opened in new tab");
                            
                            if (!newWindow || newWindow.closed || typeof newWindow.closed=='undefined') {
                                console.warn("Preview window may have been blocked by popup blocker");
                                // Show a message about popup blocker
                                alert("Preview window may have been blocked. Please click the 'Open PDF Preview' button below.");
                            }
                        } else {
                            // User prefers direct navigation
                            window.location.href = previewUrl;
                            return; // Exit early since we're redirecting
                        }
                    } catch (err) {
                        console.error("Error opening preview window:", err);
                        // The fallback UI is already in place, so no need for an error message
                    }
                } else {
                    // Fallback to table view if no PDF URL is provided
                    // Create preview table
                    let tableHtml = '<table>';
                    
                    // Add headers
                    tableHtml += '<thead><tr>';
                    for (const header of data.headers) {
                        tableHtml += `<th>${header}</th>`;
                    }
                    tableHtml += '</tr></thead>';
                    
                    // Add rows
                    tableHtml += '<tbody>';
                    for (const row of data.rows) {
                        tableHtml += '<tr>';
                        for (const cell of row) {
                            tableHtml += `<td>${cell}</td>`;
                        }
                        tableHtml += '</tr>';
                    }
                    tableHtml += '</tbody></table>';
                    
                    // Add metadata
                    tableHtml += '<div style="margin-top: 20px;">';
                    tableHtml += '<h3>Metadata</h3>';
                    tableHtml += '<ul>';
                    for (const [key, value] of Object.entries(data.metadata || {})) {
                        tableHtml += `<li><strong>${key}:</strong> ${value}</li>`;
                    }
                    tableHtml += '</ul></div>';
                    
                    previewData.innerHTML = tableHtml;
                    previewSection.classList.remove('hidden');
                }
                
            } catch (error) {
                showError(error.message || 'Error generating preview');
                console.error('Preview error:', error);
            } finally {
                // Reset previewing state
                previewButton.disabled = false;
                previewIcon.textContent = '👁️';
                previewButton.textContent = ' Preview';
            }
        });
    }
    
    // Close Preview Button
    const closePreview = document.getElementById('close-preview');
    if (closePreview) {
        closePreview.addEventListener('click', function() {
            document.getElementById('preview-section').classList.add('hidden');
        });
    }
    
    // PDF Preview Tab Logic
    const pdfSelector = document.getElementById('pdf-selector');
    const pdfSelectorContainer = document.getElementById('pdf-selector-container');
    const pdfContainer = document.getElementById('pdf-container');
    const pdfFrame = document.getElementById('pdf-frame');
    const noPdfs = document.getElementById('no-pdfs');
    const pdfLoader = document.getElementById('pdf-loader');
    const pdfControls = document.getElementById('pdf-controls');
    const openPdfBtn = document.getElementById('open-pdf-btn');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    const refreshPdfBtn = document.getElementById('refresh-pdf-btn');
    const pdfErrorMessage = document.getElementById('pdf-error-message');
    
    let pdfs = [];
    
    // Event handler for PDF updates
    window.addEventListener('pdfUpdated', function(event) {
        if (event.detail && event.detail.pdfUrl) {
            console.log('PDF updated event received:', event.detail.pdfUrl);
            
            // If we're on the PDF preview tab, refresh the PDF list
            const previewTab = document.querySelector('.tab[data-tab="preview"]');
            if (previewTab && previewTab.classList.contains('active')) {
                fetchPdfs();
            }
        }
    });
    
    // Fetch all available PDF files
    async function fetchPdfs() {
        if (!pdfLoader) return; // Not on the PDF preview page
        
        showPdfLoader();
        hidePdfError();
        
        try {
            const response = await fetch('/api/latest-pdfs');
            
            if (response.ok) {
                const data = await response.json();
                
                if (data && data.pdfs && data.pdfs.length > 0) {
                    pdfs = data.pdfs;
                    populatePdfSelector();
                    showPdfPreview(pdfs[0]);
                    hidePdfLoader();
                    hideNoPdfs();
                } else {
                    showNoPdfs();
                    hidePdfLoader();
                }
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Could not load PDFs');
            }
        } catch (err) {
            console.error('Error fetching PDFs:', err);
            showPdfError('Could not load PDF files. Please try processing a file first.');
            hidePdfLoader();
        }
    }
    
    // Populate the PDF selector dropdown
    function populatePdfSelector() {
        if (!pdfSelector) return;
        
        pdfSelector.innerHTML = '';
        
        pdfs.forEach(pdf => {
            const option = document.createElement('option');
            option.value = pdf;
            option.textContent = pdf;
            pdfSelector.appendChild(option);
        });
        
        if (pdfs.length > 1) {
            pdfSelectorContainer.classList.remove('hidden');
        } else {
            pdfSelectorContainer.classList.add('hidden');
        }
    }
    
    // Show the PDF preview
    function showPdfPreview(pdfFilename) {
        if (!pdfFrame) return;
        
        const pdfUrl = `/api/download/${pdfFilename}`;
        pdfFrame.src = pdfUrl;
        pdfContainer.classList.remove('hidden');
        pdfControls.classList.remove('hidden');
        
        openPdfBtn.href = pdfUrl;
        downloadPdfBtn.href = pdfUrl;
    }
    
    // Show PDF loader
    function showPdfLoader() {
        if (pdfLoader) pdfLoader.classList.remove('hidden');
        if (pdfContainer) pdfContainer.classList.add('hidden');
        if (pdfControls) pdfControls.classList.add('hidden');
    }
    
    // Hide PDF loader
    function hidePdfLoader() {
        if (pdfLoader) pdfLoader.classList.add('hidden');
    }
    
    // Show no PDFs message
    function showNoPdfs() {
        if (noPdfs) noPdfs.classList.remove('hidden');
        if (pdfContainer) pdfContainer.classList.add('hidden');
        if (pdfControls) pdfControls.classList.add('hidden');
        if (pdfSelectorContainer) pdfSelectorContainer.classList.add('hidden');
    }
    
    // Hide no PDFs message
    function hideNoPdfs() {
        if (noPdfs) noPdfs.classList.add('hidden');
    }
    
    // Show PDF error message
    function showPdfError(message) {
        if (pdfErrorMessage) {
            pdfErrorMessage.textContent = message;
            pdfErrorMessage.classList.remove('hidden');
        }
    }
    
    // Hide PDF error message
    function hidePdfError() {
        if (pdfErrorMessage) pdfErrorMessage.classList.add('hidden');
    }
    
    // Show error message
    function showError(message) {
        if (errorMessage) {
            errorMessage.textContent = message;
            errorMessage.classList.remove('hidden');
        }
    }
    
    // Hide error message
    function hideError() {
        if (errorMessage) errorMessage.classList.add('hidden');
    }
    
    // PDF Selector change handler
    if (pdfSelector) {
        pdfSelector.addEventListener('change', function() {
            showPdfPreview(this.value);
        });
    }
    
    // Refresh PDFs button
    if (refreshPdfBtn) {
        refreshPdfBtn.addEventListener('click', function() {
            fetchPdfs();
        });
    }
    
    // Initialize - If we're on the PDF preview tab, fetch PDFs
    const previewTab = document.querySelector('.tab.active[data-tab="preview"]');
    if (previewTab) {
        fetchPdfs();
    }
});