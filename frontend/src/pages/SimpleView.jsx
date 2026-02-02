import React, { useState, useEffect } from 'react';
import { getCategories, getSimpleRecommendation } from '../api/client';

function SimpleView() {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await getCategories();
      setCategories(response.data);
    } catch (err) {
      setError('Failed to load categories');
    }
  };

  const handleQuery = async () => {
    if (!selectedCategory) {
      setError('Please select a category');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await getSimpleRecommendation(parseInt(selectedCategory));
      setResult(response.data);
    } catch (err) {
      setError('Failed to get recommendation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="simple-view">
      <div className="search-box">
        <select
          value={selectedCategory}
          onChange={(e) => {
            setSelectedCategory(e.target.value);
            setResult(null);
          }}
          style={{ marginBottom: '1rem' }}
        >
          <option value="">Select a category...</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>
        <button
          className="btn btn-primary"
          onClick={handleQuery}
          disabled={loading}
          style={{ width: '100%', padding: '1rem', fontSize: '1.25rem' }}
        >
          {loading ? 'Loading...' : 'Find Best Card'}
        </button>
      </div>

      {error && (
        <div style={{ backgroundColor: '#fee2e2', color: '#991b1b', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}>
          {error}
        </div>
      )}

      {result && (
        <div className="result-card">
          <p style={{ fontSize: '1rem', color: '#6b7280', marginBottom: '0.5rem' }}>
            For {result.category}, use:
          </p>
          <h2>{result.card_name}</h2>
          <div className="details">
            <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#10b981', marginBottom: '0.5rem' }}>
              {result.effective_value.toFixed(2)}¢ per dollar
            </p>
            {result.details && (
              <p style={{ fontSize: '1rem' }}>{result.details}</p>
            )}
          </div>
          <button
            className="btn btn-secondary"
            style={{ marginTop: '1.5rem', padding: '0.75rem 2rem' }}
            onClick={() => setResult(null)}
          >
            Search Again
          </button>
        </div>
      )}

      {!result && (
        <div style={{ textAlign: 'center', color: 'white', marginTop: '2rem' }}>
          <p style={{ fontSize: '1.25rem', opacity: 0.9 }}>
            Select a category and find out which card to use!
          </p>
        </div>
      )}
    </div>
  );
}

export default SimpleView;
