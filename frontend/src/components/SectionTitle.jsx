import "../styles/sectionTitle.css";

function SectionTitle({ title, subtitle, className = "" }) {
  return (
    <div className={`section-title-block ${className}`.trim()}>
      <h2 className="section-title">{title}</h2>
      {subtitle && <p className="section-subtitle">{subtitle}</p>}
    </div>
  );
}

export default SectionTitle;
