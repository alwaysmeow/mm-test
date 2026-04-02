import { useEffect, useMemo, useState } from "react";

import CarCard from "./components/CarCard";
import CatalogHero from "./components/CatalogHero";
import FiltersPanel from "./components/FiltersPanel";
import ResultsToolbar from "./components/ResultsToolbar";
import SiteHeader from "./components/SiteHeader";
import StatusPanel from "./components/StatusPanel";
import { getOriginLabel, parseUsdPrice } from "./utils/carFormatters";

async function fetchJson(source, { timeoutMs = 0 } = {}) {
  const controller = new AbortController();
  const timeoutId =
    timeoutMs > 0 ? window.setTimeout(() => controller.abort(), timeoutMs) : null;

  try {
    const response = await fetch(source, { signal: controller.signal });
    if (!response.ok) {
      throw new Error(`${source} failed with status ${response.status}`);
    }
    return await response.json();
  } finally {
    if (timeoutId !== null) {
      window.clearTimeout(timeoutId);
    }
  }
}

function App() {
  const [payload, setPayload] = useState(null);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [selectedBrand, setSelectedBrand] = useState("all");
  const [selectedFuel, setSelectedFuel] = useState("all");
  const [selectedOrigin, setSelectedOrigin] = useState("all");
  const [sortBy, setSortBy] = useState("newest");

  useEffect(() => {
    let cancelled = false;

    async function loadCars() {
      try {
        setStatus("loading");
        let data = null;
        let lastError = null;

        try {
          data = await fetchJson("/cars", { timeoutMs: 1500 });
        } catch (apiError) {
          lastError = apiError;
        }

        if (!data) {
          try {
            data = await fetchJson("/cars.json");
          } catch (staticError) {
            lastError = staticError;
          }
        }

        if (!data) {
          throw lastError ?? new Error("No data source available");
        }

        if (!cancelled) {
          setPayload(data);
          setStatus("ready");
        }
      } catch (err) {
        if (!cancelled) {
          setStatus("error");
          setError(err instanceof Error ? err.message : "Unknown error");
        }
      }
    }

    loadCars();
    return () => {
      cancelled = true;
    };
  }, []);

  const cars = payload?.cars ?? [];

  const brands = useMemo(() => {
    return ["all", ...new Set(cars.map((car) => car.brand).filter(Boolean))].slice(0, 40);
  }, [cars]);

  const fuelTypes = useMemo(() => {
    return ["all", ...new Set(cars.map((car) => car.fuel_type).filter(Boolean))];
  }, [cars]);

  const filteredCars = useMemo(() => {
    const query = search.trim().toLowerCase();

    const result = cars.filter((car) => {
      if (selectedBrand !== "all" && car.brand !== selectedBrand) return false;
      if (selectedFuel !== "all" && car.fuel_type !== selectedFuel) return false;

      if (selectedOrigin !== "all") {
        const origin = getOriginLabel(car.source_kind);
        if (origin !== selectedOrigin) return false;
      }

      if (!query) return true;

      const haystack = [
        car.brand,
        car.model,
        car.location,
        car.fuel_type,
        car.source_kind,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return haystack.includes(query);
    });

    result.sort((left, right) => {
      const leftPrice = parseUsdPrice(left.price) ?? -1;
      const rightPrice = parseUsdPrice(right.price) ?? -1;
      const leftYear = left.year ?? -1;
      const rightYear = right.year ?? -1;

      if (sortBy === "price_asc") return leftPrice - rightPrice;
      if (sortBy === "price_desc") return rightPrice - leftPrice;
      if (sortBy === "year_asc") return leftYear - rightYear;
      return rightYear - leftYear;
    });

    return result;
  }, [cars, search, selectedBrand, selectedFuel, selectedOrigin, sortBy]);

  const summary = useMemo(() => {
    const newest = filteredCars
      .map((car) => car.year)
      .filter((year) => typeof year === "number")
      .sort((a, b) => b - a)[0];

    return {
      total: filteredCars.length,
      newest: newest ?? "N/A",
    };
  }, [filteredCars]);

  return (
    <div className="catalog-page">
      <SiteHeader />
      <div className="catalog-shell">
        <CatalogHero />

        <div className="catalog-layout">
          <FiltersPanel
            search={search}
            onSearchChange={setSearch}
            brands={brands}
            selectedBrand={selectedBrand}
            onBrandChange={setSelectedBrand}
            fuelTypes={fuelTypes}
            selectedFuel={selectedFuel}
            onFuelChange={setSelectedFuel}
            selectedOrigin={selectedOrigin}
            onOriginChange={setSelectedOrigin}
            onReset={() => {
              setSearch("");
              setSelectedBrand("all");
              setSelectedFuel("all");
              setSelectedOrigin("all");
              setSortBy("newest");
            }}
          />

          <main className="catalog-main">
            <ResultsToolbar
              total={summary.total}
              newest={summary.newest}
              sortBy={sortBy}
              onSortChange={setSortBy}
            />

            {status === "loading" && (
              <StatusPanel>Loading inventory from the API...</StatusPanel>
            )}

            {status === "error" && (
              <StatusPanel error>Failed to load `/cars`: {error}</StatusPanel>
            )}

            {status === "ready" && (
              <section className="cards-grid">
                {filteredCars.map((car) => (
                  <CarCard key={car.car_id} car={car} />
                ))}
              </section>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;
