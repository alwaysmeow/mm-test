import { formatMileage, formatPrice, getOriginLabel } from "../utils/carFormatters";

function CarCard({ car }) {
  return (
    <article className="listing-card">
      <div className="listing-media">
        <img
          src={car.photo_url}
          alt={`${car.brand ?? "Vehicle"} ${car.model ?? ""}`.trim()}
          loading="lazy"
        />
        <span className="origin-badge">{getOriginLabel(car.source_kind)}</span>
      </div>

      <div className="listing-body">
        <div className="listing-title">
          <p>{car.brand ?? "Unknown brand"}</p>
          <h2>{car.model ?? "Unnamed vehicle"}</h2>
        </div>

        <div className="listing-specs">
          <div>
            <span>Year</span>
            <strong>{car.year ?? "N/A"}</strong>
          </div>
          <div>
            <span>Mileage</span>
            <strong>{formatMileage(car.mileage_km)}</strong>
          </div>
          <div>
            <span>Fuel</span>
            <strong>{car.fuel_type ?? "N/A"}</strong>
          </div>
        </div>

        <div className="listing-bottom">
          <div className="price-block">
            <span>Price</span>
            <strong>{formatPrice(car.price)}</strong>
          </div>

          <a
            className="details-link"
            href={car.source_url || "#"}
            target="_blank"
            rel="noreferrer"
          >
            Details
          </a>
        </div>

        <p className="location-text">{car.location ?? "Location N/A"}</p>
      </div>
    </article>
  );
}

export default CarCard;
