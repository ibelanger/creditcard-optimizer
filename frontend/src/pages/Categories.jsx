import React, { useState, useEffect } from 'react';
import { getCategories, createCategory, updateCategory, deleteCategory } from '../api/client';

function Categories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAdd, setShowAdd] = useState(false);
  const [newCategory, setNewCategory] = useState({ name: '', description: '' });

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const response = await getCategories();
      setCategories(response.data);
    } catch (err) {
      setError('Failed to load categories');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    if (!newCategory.name) {
      setError('Category name is required');
      return;
    }

    try {
      await createCategory(newCategory);
      setShowAdd(false);
      setNewCategory({ name: '', description: '' });
      loadCategories();
    } catch (err) {
      setError('Failed to add category');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this category?')) return;

    try {
      await deleteCategory(id);
      loadCategories();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete category');
    }
  };

  if (loading) return <div className="container"><div className="loading">Loading...</div></div>;

  return (
    <div className="container">
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Categories</h2>
          <button className="btn btn-primary" onClick={() => setShowAdd(!showAdd)}>
            {showAdd ? 'Cancel' : 'Add Category'}
          </button>
        </div>

        {error && <div className="error">{error}</div>}

        {showAdd && (
          <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
            <h3>Add New Category</h3>
            <div className="form-group">
              <label>Category Name</label>
              <input
                type="text"
                value={newCategory.name}
                onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
                placeholder="e.g., Gas - Pump"
              />
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={newCategory.description}
                onChange={(e) => setNewCategory({ ...newCategory, description: e.target.value })}
                placeholder="Optional description"
                rows="2"
              />
            </div>
            <button className="btn btn-success" onClick={handleAdd}>
              Save Category
            </button>
          </div>
        )}

        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Description</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {categories.map((cat) => (
              <tr key={cat.id}>
                <td>{cat.name}</td>
                <td>{cat.description || '-'}</td>
                <td>
                  <button className="btn btn-danger" onClick={() => handleDelete(cat.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Categories;
