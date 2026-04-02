function FiltersPanel({
  search,
  onSearchChange,
  brands,
  selectedBrand,
  onBrandChange,
  fuelTypes,
  selectedFuel,
  onFuelChange,
  selectedOrigin,
  onOriginChange,
  onReset,
}) {
  const originOptions = [
    { value: "all", label: "All" },
    { value: "Korean", label: "Korean" },
    { value: "Imported", label: "Imported" },
  ];

  return (
    <section className="filters-panel">
      <div className="filters-grid">
        <label className="field-block field-search">
          <span>Search</span>
          <input
            type="search"
            placeholder="BMW, Seoul, electric..."
            value={search}
            onChange={(event) => onSearchChange(event.target.value)}
          />
        </label>

        <label className="field-block">
          <span>Brand</span>
          <select value={selectedBrand} onChange={(event) => onBrandChange(event.target.value)}>
            {brands.map((brand) => (
              <option key={brand} value={brand}>
                {brand}
              </option>
            ))}
          </select>
        </label>

        <label className="field-block">
          <span>Fuel Type</span>
          <select value={selectedFuel} onChange={(event) => onFuelChange(event.target.value)}>
            {fuelTypes.map((fuel) => (
              <option key={fuel} value={fuel}>
                {fuel}
              </option>
            ))}
          </select>
        </label>

        <div className="field-block">
          <span>Origin</span>
          <div className="segmented">
            {originOptions.map((item) => (
              <button
                key={item.value}
                type="button"
                className={selectedOrigin === item.value ? "segment active" : "segment"}
                onClick={() => onOriginChange(item.value)}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <div className="filters-actions">
          <button type="button" className="reset-button" onClick={onReset}>
            Reset
          </button>
        </div>
      </div>
    </section>
  );
}

export default FiltersPanel;
