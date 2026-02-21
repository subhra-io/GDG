'use client';

import { useState } from 'react';
import { uploadPolicy, extractRules } from '@/lib/api';

export default function PolicyUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [policyId, setPolicyId] = useState<string | null>(null);
  const [message, setMessage] = useState<string>('');
  const [rulesCount, setRulesCount] = useState<number>(0);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setMessage('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select a file');
      return;
    }

    setUploading(true);
    setMessage('');

    try {
      const response = await uploadPolicy(file);
      setPolicyId(response.data.id);
      setMessage('Policy uploaded successfully! Click "Extract Rules" to continue.');
    } catch (error: any) {
      setMessage(`Upload failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleExtractRules = async () => {
    if (!policyId) return;

    setExtracting(true);
    setMessage('Extracting rules with AI... This may take 10-15 seconds.');

    try {
      const response = await extractRules(policyId);
      setRulesCount(response.data.rules_extracted);
      setMessage(`Successfully extracted ${response.data.rules_extracted} rules!`);
    } catch (error: any) {
      setMessage(`Extraction failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setExtracting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Upload Policy Document</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select PDF File
          </label>
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-md file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
          />
        </div>

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {uploading ? 'Uploading...' : 'Upload Policy'}
        </button>

        {policyId && (
          <button
            onClick={handleExtractRules}
            disabled={extracting}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {extracting ? 'Extracting Rules...' : 'Extract Rules with AI'}
          </button>
        )}

        {message && (
          <div className={`p-4 rounded-md ${
            message.includes('failed') || message.includes('error')
              ? 'bg-red-50 text-red-800'
              : 'bg-green-50 text-green-800'
          }`}>
            {message}
          </div>
        )}

        {rulesCount > 0 && (
          <div className="bg-blue-50 p-4 rounded-md">
            <p className="text-sm text-blue-800">
              <strong>{rulesCount} rules</strong> extracted and ready for compliance monitoring.
              Go to the Dashboard to scan for violations.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
