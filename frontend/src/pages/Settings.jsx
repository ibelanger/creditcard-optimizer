import React, { useState, useEffect } from 'react';
import { getCurrencies, createCurrency, updateCurrency, deleteCurrency } from '../api/client';

function Settings() {
  const [currencies, setCurrencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [newCurrency, setNewCurrency] = useState({ name: '', cpp_value: 1.0 });
  const [editing, setEditing] = useState(null);

  useEffect(() => {
    loadCurrencies();
  }, []);

  const loadCurrencies = async () => {
    try {
      const response = await getCurrencies();
      setCurrencies(response.data);
    } catch (err) {
      setError('Failed to load currencies');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    if (!newCurrency.name) {
      setError('Currency name is required');
      return;
    }

    try {
      await createCurrency(newCurrency);
      setShowAdd(false);
      setNewCurrency({ name: '', cpp_value: 1.0 });
      loadCurrencies();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add currency');
    }
  };

  const handleUpdate = async (id, cpp_value) => {
    try {
      await updateCurrency(id, { cpp_value: parseFloat(cpp_value) });
      setEditing(null);
      loadCurrencies();
    } catch (err) {
      setError('Failed to update currency');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this currency?')) return;

    try {
      await deleteCurrency(id);
      loadCurrencies();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete currency');
    }
  };

  if (loading) return <div className="container"><div className="loading">Loading...</div></div>;

  return (
    <div className="container">
      <div className="card">
        <h2>Point Currency Settings</h2>
        <p style={{ color: '#6b7280', marginBottom: '1rem' }}>
          Manage your point currencies and their cents-per-point (CPP) valuations.
        </p>

        {error && <div className="error">{error}</div>}

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
          <button className="btn btn-primary" onClick={() => setShowAdd(!showAdd)}>
            {showAdd ? 'Cancel' : 'Add Currency'}
          </button>
        </div>

        {showAdd && (
          <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f9fafb', borderRadius: '8px', marginBottom: '1rem' }}>
            <h3>Add New Currency</h3>
            <div className="form-group">
              <label>Currency Name</label>
              <input
                type="text"
                value={newCurrency.name}
                onChange={(e) => setNewCurrency({ ...newCurrency, name: e.target.value })}
                placeholder="e.g., Chase UR"
              />
            </div>
            <div className="form-group">
              <label>CPP Value (cents per point)</label>
              <input
                type="number"
                step="0.1"
                value={newCurrency.cpp_value}
                onChange={(e) => setNewCurrency({ ...newCurrency, cpp_value: parseFloat(e.target.value) })}
              />
            </div>
            <button className="btn btn-success" onClick={handleAdd}>
              Save Currency
            </button>
          </div>
        )}

        <table className="table">
          <thead>
            <tr>
              <th>Currency Name</th>
              <th>CPP Value</th>
              <th>Last Updated</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {currencies.map((currency) => (
              <tr key={currency.id}>
                <td>{currency.name}</td>
                <td>
                  {editing === currency.id ? (
                    <input
                      type="number"
                      step="0.1"
                      defaultValue={currency.cpp_value}
                      id={`cpp-${currency.id}`}
                      style={{ width: '100px' }}
                    />
                  ) : (
                    `${currency.cpp_value}¢`
                  )}
                </td>
                <td>{new Date(currency.updated_at).toLocaleDateString()}</td>
                <td>
                  {editing === currency.id ? (
                    <>
                      <button
                        className="btn btn-success"
                        style={{ marginRight: '0.5rem' }}
                        onClick={() => {
                          const value = document.getElementById(`cpp-${currency.id}`).value;
                          handleUpdate(currency.id, value);
                        }}
                      >
                        Save
                      </button>
                      <button className="btn btn-secondary" onClick={() => setEditing(null)}>
                        Cancel
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        className="btn btn-secondary"
                        style={{ marginRight: '0.5rem' }}
                        onClick={() => setEditing(currency.id)}
                      >
                        Edit CPP
                      </button>
                      <button className="btn btn-danger" onClick={() => handleDelete(currency.id)}>
                        Delete
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2>Backup & Data</h2>
        <p style={{ color: '#6b7280', marginBottom: '1rem' }}>
          Your data is stored in a SQLite database at <code>data/cards.db</code>.
          You can backup this file manually or use your NAS backup solution.
        </p>
      </div>
    </div>
  );
}

export default Settings;
