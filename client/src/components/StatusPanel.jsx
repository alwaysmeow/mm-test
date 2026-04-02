function StatusPanel({ children, error = false }) {
  return (
    <section className={error ? "status-panel status-error" : "status-panel"}>
      {children}
    </section>
  );
}

export default StatusPanel;
