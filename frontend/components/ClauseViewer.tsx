'use client';

import { useState, useEffect } from 'react';

interface ClauseViewerProps {
  policyId: string;
  pageNumber: number;
  clauseText: string;
  onClose: () => void;
}

export default function ClauseViewer({
  policyId,
  pageNumber,
  clauseText,
  onClose
}: ClauseViewerProps) {
  const [loading, setLoading] = useState(true);
  const [pageText, setPageText] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPageText();
  }, [policyId, pageNumber]);

  const fetchPageText = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:8000/api/v1/policies/${policyId}/page/${pageNumber}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch page');
      }
      
      const data = await response.json();
      setPageText(data.text);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load page');
    } finally {
      setLoading(false);
    }
  };

  const highlightClause = (text: string) => {
    if (!clauseText) return text;
    
    const index = text.toLowerCase().indexOf(clauseText.toLowerCase());
    if (index === -1) return text;

    const before = text.substring(0, index);
    const clause = text.substring(index, index + clauseText.length);
    const after = text.substring(index + clauseText.length);

    return (
      <>
        {before}
        <mark className="bg-yellow-200 font-semibold">{clause}</mark>
        {after}
      </>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[85vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b flex justify-between items-center bg-gray-50">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Policy Document - Page {pageNumber}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Viewing clause reference
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading page...</p>
              </div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">{error}</p>
              <button
                onClick={fetchPageText}
                className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
              >
                Try again
              </button>
            </div>
          ) : (
            <div className="prose max-w-none">
              <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-gray-800">
                  {highlightClause(pageText)}
                </pre>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t bg-gray-50 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            {clauseText && (
              <span>
                <span className="font-medium">Highlighted:</span> "{clauseText.substring(0, 50)}
                {clauseText.length > 50 ? '...' : ''}"
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
