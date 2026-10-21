import React from 'react';

export default function StarRating({ rating = 0, max = 5, interactive = false, onChange }) {
  const numericRating = Number(rating) || 0;
  
  if (interactive) {
    return (
      <div className="star-rating-picker">
        {[1, 2, 3, 4, 5].map((val) => (
          <button
            type="button"
            key={val}
            className={`star-btn ${numericRating === val ? 'selected' : ''}`}
            onClick={() => onChange && onChange(val)}
          >
            ★ {val} {val === 5 ? '(Excellent)' : val === 1 ? '(Poor)' : ''}
          </button>
        ))}
      </div>
    );
  }

  // Display only
  const stars = [];
  for (let i = 1; i <= max; i++) {
    if (i <= Math.round(numericRating)) {
      stars.push(<span key={i} style={{ color: '#ecc94b', fontSize: '1.2rem' }}>★</span>);
    } else {
      stars.push(<span key={i} style={{ color: '#cbd5e0', fontSize: '1.2rem' }}>☆</span>);
    }
  }

  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '2px' }}>
      {stars}
      <strong style={{ marginLeft: '6px', fontSize: '0.95rem' }}>{numericRating.toFixed(1)}/5</strong>
    </span>
  );
}
