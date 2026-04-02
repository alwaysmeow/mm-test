function ResultsToolbar({ total, newest, sortBy, onSortChange }) {
  return (
    <section className="results-toolbar">
      <div className="results-meta">
        <p>{total} cars found</p>
        <span>Newest year: {newest}</span>
      </div>

      <label className="sort-field">
        <span>Sort by</span>
        <select value={sortBy} onChange={(event) => onSortChange(event.target.value)}>
          <option value="newest">Year: New to Old</option>
          <option value="year_asc">Year: Old to New</option>
          <option value="price_asc">Price: Low to High</option>
          <option value="price_desc">Price: High to Low</option>
        </select>
      </label>
    </section>
  );
}

export default ResultsToolbar;
