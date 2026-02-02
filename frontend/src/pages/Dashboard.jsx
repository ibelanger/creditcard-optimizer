import React, { useState, useEffect } from 'react';
import { getCategories, getRecommendations } from '../api/client';

function Dashboard() {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [recommendations, setRecommendations] = useState(null);
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
      const response = await getRecommendations({ category_id: parseInt(selectedCategory) });
      setRecommendations(response.data);
    } catch (err) {
      setError('Failed to get recommendations');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h2>Quick Query</h2>
        <div className="form-group">
          <label>Select Category</label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="">Choose a category...</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>
        <button className="btn btn-primary" onClick={handleQuery} disabled={loading}>
          {loading ? 'Loading...' : 'Get Recommendations'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {recommendations && (
        <div className="card">
          <h2>Recommendations for {recommendations.category}</h2>
          {recommendations.recommendations.map((rec) => (
            <div
              key={rec.rank}
              className={`recommendation-card ${rec.rank === 1 ? 'top-pick' : ''}`}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                <div>
                  <h3>
                    #{rec.rank} - {rec.card_name}
                  </h3>
                  <p>
                    <strong>Effective Value:</strong> {rec.effective_value.toFixed(2)}¢ per dollar
                  </p>
                  <p>
                    <strong>Reward Rate:</strong> {rec.reward_rate}% {rec.currency}
                  </p>
                  <p>
                    <strong>CPP Value:</strong> {rec.cpp.toFixed(2)}¢
                  </p>
                  {rec.cap_status && (
                    <p className={rec.cap_warning ? 'badge badge-warning' : 'badge badge-success'}>
                      {rec.cap_status}
                    </p>
                  )}
                </div>
                {rec.rank === 1 && (
                  <span className="badge badge-success" style={{ fontSize: '1rem' }}>
                    TOP PICK
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Dashboard;
