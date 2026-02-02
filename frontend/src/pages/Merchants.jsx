import React, { useState, useEffect } from 'react';
import { getMerchants, getCategories, createMerchant, updateMerchant, deleteMerchant } from '../api/client';

function Merchants() {
  const [merchants, setMerchants] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [newMerchant, setNewMerchant] = useState({ name: '', category_id: '' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [merchantsRes, categoriesRes] = await Promise.all([
        getMerchants(),
        getCategories(),
      ]);
      setMerchants(merchantsRes.data);
      setCategories(categoriesRes.data);
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    if (!newMerchant.name || !newMerchant.category_id) {
      setError('Merchant name and category are required');
      return;
    }

    try {
      await createMerchant({
        ...newMerchant,
        category_id: parseInt(newMerchant.category_id),
      });
      setShowAdd(false);
      setNewMerchant({ name: '', category_id: '' });
      loadData();
    } catch (err) {
      setError('Failed to add merchant');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this merchant?')) return;

    try {
      await deleteMerchant(id);
      loadData();
    } catch (err) {
      setError('Failed to delete merchant');
    }
  };

  if (loading) return <div className="container"><div className="loading">Loading...</div></div>;

  return (
    <div className="container">
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Merchants</h2>
          <button className="btn btn-primary" onClick={() => setShowAdd(!showAdd)}>
            {showAdd ? 'Cancel' : 'Add Merchant'}
          </button>
        </div>

        {error && <div className="error">{error}</div>}

        {showAdd && (
          <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
            <h3>Add New Merchant</h3>
            <div className="form-group">
              <label>Merchant Name</label>
              <input
                type="text"
                value={newMerchant.name}
                onChange={(e) => setNewMerchant({ ...newMerchant, name: e.target.value })}
                placeholder="e.g., Costco Gas"
              />
            </div>
            <div className="form-group">
              <label>Default Category</label>
              <select
                value={newMerchant.category_id}
                onChange={(e) => setNewMerchant({ ...newMerchant, category_id: e.target.value })}
              >
                <option value="">Select category...</option>
                {categories.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>
            <button className="btn btn-success" onClick={handleAdd}>
              Save Merchant
            </button>
          </div>
        )}

        <table className="table">
          <thead>
            <tr>
              <th>Merchant Name</th>
              <th>Category</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {merchants.map((merchant) => (
              <tr key={merchant.id}>
                <td>{merchant.name}</td>
                <td>{merchant.category_name}</td>
                <td>
                  <button className="btn btn-danger" onClick={() => handleDelete(merchant.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {merchants.length === 0 && (
          <p style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
            No merchants added yet. Add merchants to quickly map them to categories.
          </p>
        )}
      </div>
    </div>
  );
}

export default Merchants;
