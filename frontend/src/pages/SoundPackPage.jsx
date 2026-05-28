import PackHeader from "../components/PackHeader";
import PackTrack from "../components/PackTrack";
import PackSidebar from "../components/PackSidebar";
import PackReview from "../components/PackReview";

import "../styles/soundpack.css";

function SoundPackPage() {
  return (
    <div className="soundpack-page">

      <div className="soundpack-layout">

        <div className="soundpack-main">

          <PackHeader />

          <h2 className="section-title">Содержимое пакета</h2>

          <div className="pack-tracks">

            <PackTrack />
            <PackTrack />
            <PackTrack />
            <PackTrack />
            <PackTrack />

          </div>

        </div>

        <div className="soundpack-sidebar">

          <PackSidebar />

          <h3 className="review-title">Отзывы</h3>

          <PackReview />
          <PackReview />

        </div>

      </div>

    </div>
  );
}

export default SoundPackPage;