import { useNavigate } from "react-router-dom";
import { FeatureCards } from "../components/FeatureCards";
import { HeroSection } from "../components/HeroSection";

export function Home() {
  const navigate = useNavigate();

  const handleAnalyze = (handle: string) => {
    navigate(`/dashboard/${encodeURIComponent(handle)}`);
  };

  return (
    <div className="space-y-8">
      <HeroSection onAnalyze={handleAnalyze} />
      <FeatureCards />
    </div>
  );
}
