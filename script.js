// ── MomCare Shared Script ──

// Generate floating petals background
function generatePetals(containerId = 'petals', count = 16) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const colors = ['#e0c8f5','#f5c6d0','#c8e0f5','#f5e0c8','#d4f0e8'];
  for (let i = 0; i < count; i++) {
    const p = document.createElement('div');
    p.className = 'petal';
    p.style.cssText = `
      left: ${Math.random() * 100}vw;
      background: ${colors[Math.floor(Math.random() * colors.length)]};
      width: ${8 + Math.random() * 8}px;
      height: ${12 + Math.random() * 10}px;
      animation-duration: ${6 + Math.random() * 8}s;
      animation-delay: ${Math.random() * 7}s;
      border-radius: ${Math.random() > 0.5 ? '50% 0 50% 0' : '0 50% 0 50%'};
    `;
    container.appendChild(p);
  }
}

// Save to localStorage with prefix
function momStore(key, value) {
  localStorage.setItem(`momcare_${key}`, JSON.stringify(value));
}
function momLoad(key, fallback = null) {
  const val = localStorage.getItem(`momcare_${key}`);
  return val ? JSON.parse(val) : fallback;
}

// Get risk level from score (0–15)
function getRiskLevel(score) {
  if (score >= 11) return 'low';
  if (score >= 6) return 'moderate';
  return 'high';
}

// Format seconds to mm:ss
function formatTime(seconds) {
  const m = String(Math.floor(seconds / 60)).padStart(2, '0');
  const s = String(seconds % 60).padStart(2, '0');
  return `${m}:${s}`;
}

// Get greeting based on time
function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return 'Good Morning';
  if (h < 17) return 'Good Afternoon';
  return 'Good Evening';
}

// Daily affirmations pool
const AFFIRMATIONS = [
  '"You are enough. You have always been enough."',
  '"Rest is not a reward — it is part of healing."',
  '"Every moment of doubt you overcome makes you stronger."',
  '"Your baby chose you. And they chose perfectly."',
  '"Asking for help is courage, not weakness."',
  '"You are growing into the mother your child needs."',
  '"Your feelings are valid. All of them."',
  '"Small steps are still steps forward, mama."',
  '"You don\'t have to do it all. You just have to be there."',
  '"Love doesn\'t have to be perfect to be real."',
];

function getRandomAffirmation() {
  return AFFIRMATIONS[Math.floor(Math.random() * AFFIRMATIONS.length)];
}