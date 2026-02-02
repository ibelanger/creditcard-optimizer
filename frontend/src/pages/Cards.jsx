import React, { useState, useEffect } from 'react';
import {
  getCards,
  getCurrencies,
  getCategories,
  createCard,
  updateCard,
  deleteCard,
  addCardReward,
  updateCardReward,
  deleteCardReward,
} from '../api/client';

function Cards() {
  const [cards, setCards] = useState([]);
  const [currencies, setCurrencies] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showAddCard, setShowAddCard] = useState(false);
  const [editingCard, setEditingCard] = useState(null);
  const [newCard, setNewCard] = useState({
    name: '',
    issuer: '',
    last_four: '',
    point_currency_id: '',
    default_reward_rate: 1.0,
    is_active: true,
    notes: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [cardsRes, currenciesRes, categoriesRes] = await Promise.all([
        getCards(),
        getCurrencies(),
        getCategories(),
      ]);
      setCards(cardsRes.data);
      setCurrencies(currenciesRes.data);
      setCategories(categoriesRes.data);
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddCard = async () => {
    try {
      await createCard(newCard);
      setShowAddCard(false);
      setNewCard({
        name: '',
        issuer: '',
        last_four: '',
        point_currency_id: '',
        default_reward_rate: 1.0,
        is_active: true,
        notes: '',
      });
      loadData();
    } catch (err) {
      setError('Failed to add card');
    }
  };

  const handleDeleteCard = async (id) => {
    if (!confirm('Are you sure you want to delete this card?')) return;

    try {
      await deleteCard(id);
      loadData();
    } catch (err) {
      setError('Failed to delete card');
    }
  };

  const handleToggleActive = async (card) => {
    try {
      await updateCard(card.id, { is_active: !card.is_active });
      loadData();
    } catch (err) {
      setError('Failed to update card');
    }
  };

  if (loading) return <div className="container"><div className="loading">Loading...</div></div>;

  return (
    <div className="container">
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Credit Cards</h2>
          <button className="btn btn-primary" onClick={() => setShowAddCard(!showAddCard)}>
            {showAddCard ? 'Cancel' : 'Add Card'}
          </button>
        </div>

        {error && <div className="error">{error}</div>}

        {showAddCard && (
          <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: '#f9fafb', borderRadius: '8px' }}>
            <h3>Add New Card</h3>
            <div className="form-group">
              <label>Card Name</label>
              <input
                type="text"
                value={newCard.name}
                onChange={(e) => setNewCard({ ...newCard, name: e.target.value })}
                placeholder="e.g., Chase Freedom Flex"
              />
            </div>
            <div className="form-group">
              <label>Issuer</label>
              <input
                type="text"
                value={newCard.issuer}
                onChange={(e) => setNewCard({ ...newCard, issuer: e.target.value })}
                placeholder="e.g., Chase"
              />
            </div>
            <div className="form-group">
              <label>Last Four Digits</label>
              <input
                type="text"
                maxLength="4"
                value={newCard.last_four}
                onChange={(e) => setNewCard({ ...newCard, last_four: e.target.value })}
                placeholder="1234"
              />
            </div>
            <div className="form-group">
              <label>Point Currency</label>
              <select
                value={newCard.point_currency_id}
                onChange={(e) => setNewCard({ ...newCard, point_currency_id: parseInt(e.target.value) })}
              >
                <option value="">Select currency...</option>
                {currencies.map((curr) => (
                  <option key={curr.id} value={curr.id}>
                    {curr.name} ({curr.cpp_value}¢ per point)
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Default Reward Rate (%)</label>
              <input
                type="number"
                step="0.1"
                value={newCard.default_reward_rate}
                onChange={(e) => setNewCard({ ...newCard, default_reward_rate: parseFloat(e.target.value) })}
              />
            </div>
            <div className="form-group">
              <label>Notes</label>
              <textarea
                value={newCard.notes}
                onChange={(e) => setNewCard({ ...newCard, notes: e.target.value })}
                rows="3"
              />
            </div>
            <button className="btn btn-success" onClick={handleAddCard}>
              Save Card
            </button>
          </div>
        )}

        <table className="table">
          <thead>
            <tr>
              <th>Card Name</th>
              <th>Issuer</th>
              <th>Last 4</th>
              <th>Currency</th>
              <th>Default Rate</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {cards.map((card) => (
              <tr key={card.id}>
                <td>{card.name}</td>
                <td>{card.issuer}</td>
                <td>{card.last_four || '-'}</td>
                <td>{card.point_currency_name}</td>
                <td>{card.default_reward_rate}%</td>
                <td>
                  <span className={`badge ${card.is_active ? 'badge-success' : 'badge-warning'}`}>
                    {card.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>
                  <button
                    className="btn btn-secondary"
                    style={{ marginRight: '0.5rem' }}
                    onClick={() => handleToggleActive(card)}
                  >
                    {card.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                  <button className="btn btn-danger" onClick={() => handleDeleteCard(card.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {cards.length === 0 && <p style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>No cards added yet.</p>}
      </div>
    </div>
  );
}

export default Cards;
