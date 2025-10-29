// === Mixtli Retro UI: Music + Controller + Carousel (Scroll-Centered Version) ===
document.addEventListener("DOMContentLoaded", () => {
  const games = window.MIXTLI_GAMES || [];
  const track = document.getElementById("carousel");
  const slots = Array.from(document.querySelectorAll(".cart-slot"));
  const titleEl = document.getElementById("current-title");
  const platEl = document.getElementById("current-platform");

  const sfxMove = document.getElementById("sfx-move");
  const sfxLaunch = document.getElementById("sfx-launch");
  const bgm = document.getElementById("bgm");
  let currentIndex = 0;
  let isScrolling = false;
  let youtubePlayer = null;
  let youtubeReady = false;
  let lastInputTime = 0;
  let bootsfx = null;

window.addEventListener("load", () => {
  const power = document.getElementById("power-start");
  const overlay = document.getElementById("boot-overlay");
  const sfx = document.getElementById("boot-sfx");

  // Wait for "user gesture"
  function bootSequenceStart() {
    setTimeout(() => {
  const bgm = document.getElementById("bgm");
  if (bgm) {
    bgm.volume = 0;
    bgm.loop = true;
    bgm.play().then(() => {
      const fade = setInterval(() => {
        if (bgm.volume < 0.4) bgm.volume += 0.02;
        else clearInterval(fade);
      }, 120);
    }).catch(()=>{});
  }
}, 3500);

    // Unlock audio context naturally
    if (sfx && !bootsfx) {
      sfx.volume = 0.9;
      sfx.play().catch(() => {});
      bootsfx = 1;
    }

    // Fade out "Press Power" prompt
    power.classList.add("fade-out");

    // Trigger boot overlay animation
    overlay.style.display = "flex";
    setTimeout(() => {
      overlay.style.opacity = "1";
    }, 100);

    // Boot overlay fade-out after ~4s
    setTimeout(() => {
      overlay.style.opacity = "0";
      setTimeout(() => overlay.remove(), 1200);
    }, 4200);

    // Remove listeners
    document.removeEventListener("click", bootSequenceStart);
    document.removeEventListener("keydown", bootSequenceStart);
    window.removeEventListener("gamepadconnected", bootSequenceStart);
  }

  // Start system on click, keypress, or controller press
  document.addEventListener("click", () => {
    setTimeout(() => {
        bootSequenceStart();
    }, 850);
    });
  document.addEventListener("keydown", () => {
    setTimeout(() => {
        bootSequenceStart();
    }, 850);
    });
    window.addEventListener("gamepadconnected", () => {
    // For controllers, treat the first button press as power
    const padPoll = setInterval(() => {
      const pads = navigator.getGamepads();
      const gp = pads[0];
      if (gp && gp.buttons.some(b => b.pressed)) {
            setTimeout(() => {
                bootSequenceStart();
            }, 850);
        clearInterval(padPoll);
      }
    }, 100);
  });
});


  // === MUSIC ===
  function startBGM() {
    if (!bgm) return;
    bgm.volume = 0.4;
    bgm.loop = true;
    bgm.play().catch(err => console.log("Autoplay blocked:", err));
  }

  function fadeOutBGM() {
    if (!bgm) return;
    let vol = bgm.volume;
    const fade = setInterval(() => {
      vol -= 0.05;
      if (vol <= 0) {
        bgm.pause();
        clearInterval(fade);
      } else bgm.volume = vol;
    }, 80);
  }

  const playMove = () => sfxMove && (sfxMove.currentTime = 0, sfxMove.play().catch(()=>{}));
  const playLaunch = () => sfxLaunch && (sfxLaunch.currentTime = 0, sfxLaunch.play().catch(()=>{}));

  // === Equalizer pulse animation ===
const bars = [document.getElementById("eq1"), document.getElementById("eq2"), document.getElementById("eq3")];
let eqTimer = 0;

function updateEqualizer() {
  if (!bgm || bgm.paused) {
    bars.forEach(b => b.style.transform = "scaleY(0.2)");
  } else {
    const t = bgm.currentTime;
    // pseudo "beat" pulses based on time & random noise
    bars.forEach((bar, i) => {
      const pulse = (Math.sin(t * 3 + i) + 1) / 2 + i * 0.3;
      bar.style.transform = `scaleY(${0.3 + pulse * 1.2})`;
      bar.style.opacity = 0.6 +  1 * 0.4;
    });
  }
  requestAnimationFrame(updateEqualizer);
}
updateEqualizer();


  // === SCROLL-BASED CAROUSEL ===
  const scrollContainer = document.querySelector(".carousel-stage");

  function setActive(i) {
    if (i < 0 || i >= slots.length) return;
    currentIndex = i;
    slots.forEach(s => s.classList.remove("active"));
    const active = slots[currentIndex];
    active.classList.add("active");
    titleEl.textContent = active.dataset.title.toUpperCase();
    platEl.textContent = active.dataset.platform;
    playMove();
    smoothScrollToActive();
    tryPlayYouTubeOST(active.dataset.title);
  }

  function smoothScrollToActive() {
    const active = slots[currentIndex];
    if (!active || !scrollContainer) return;
    isScrolling = true;

    const containerRect = scrollContainer.getBoundingClientRect();
    const targetCenter = active.offsetLeft + active.offsetWidth / 2;
    const scrollTarget = targetCenter - containerRect.width / 2;

    const start = scrollContainer.scrollLeft;
    const distance = scrollTarget - start;
    const duration = 400;
    const startTime = performance.now();

    function animate(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 0.5 - Math.cos(progress * Math.PI) / 2;
      scrollContainer.scrollLeft = start + distance * ease;

      if (progress < 1) requestAnimationFrame(animate);
      else isScrolling = false;
    }
    requestAnimationFrame(animate);
  }

  function goLeft() {
    if (isScrolling) return;
    if (currentIndex > 0) setActive(currentIndex - 1);
  }

  function goRight() {
    if (isScrolling) return;
    if (currentIndex < slots.length - 1) setActive(currentIndex + 1);
  }

  function launchGame() {
    const slot = slots[currentIndex];
    const game = {
      title: slot.dataset.title,
      platform: slot.dataset.platform,
      path: slot.dataset.path
    };
    fadeOutBGM();
    fetch("/launch", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(game)
    }).then(r => r.json()).then(resp => {
      console.log(resp.message || "Launched");
      playLaunch();
    });
  }

  // === YouTube OST (Placeholder for future feature) ===
  const tag = document.createElement('script');
  tag.src = "https://www.youtube.com/iframe_api";
  document.body.appendChild(tag);

  window.onYouTubeIframeAPIReady = () => {
    youtubePlayer = new YT.Player('yt-ost', {
      height: '0',
      width: '0',
      videoId: '',
      events: { 'onReady': () => youtubeReady = true }
    });
  };

  async function tryPlayYouTubeOST(title) {
    if (!youtubeReady) return;
    console.log(`Pretend searching OST for: ${title}`);
  }

  // === INPUT HANDLERS ===
  document.addEventListener("keydown", e => {
    if (e.repeat) return;
    if (e.key === "ArrowLeft") goLeft();
    else if (e.key === "ArrowRight") goRight();
    else if (e.key === "Enter") launchGame();
  });

  slots.forEach((s, i) => s.addEventListener("click", () => setActive(i)));
  window.addEventListener("resize", smoothScrollToActive);

  setActive(0);

  // --- GAMEPAD SUPPORT ---
  let activePad = null;
  function pollGamepads() {
    const pads = navigator.getGamepads ? navigator.getGamepads() : [];
    for (let pad of pads) {
      if (pad && pad.connected) {
        activePad = pad;
        handleGamepad(pad);
      }
    }
    requestAnimationFrame(pollGamepads);
  }

  // === Dynamic OST via YouTube ===
  // inject YouTube iframe API
  tag.src = "https://www.youtube.com/iframe_api";
  document.body.appendChild(tag);

  window.onYouTubeIframeAPIReady = () => {
    youtubePlayer = new YT.Player('yt-ost', {
      height: '0', width: '0',
      videoId: '',
      events: { 'onReady': () => youtubeReady = true }
    });
  };

  // find OST
// === Dynamic OST Search + Playback (Brave Search Edition) ===
async function tryPlayYouTubeOST(title) {
  if (!youtubeReady || !youtubePlayer) return;
  try {
    const resp = await fetch(`/search_ost?title=${encodeURIComponent(title)}`);
    const data = await resp.json();

    if (data.videoId) {
      console.log(` Found OST for ${title}: ${data.videoId}`);
      if (bgm && !bgm.paused) bgm.pause();
      youtubePlayer.loadVideoById(data.videoId);
      youtubePlayer.setVolume(45);
      youtubePlayer.playVideo();
    } else {
      console.warn(`No OST found for "${title}", reverting to BGM.`);
      if (bgm.paused) bgm.play().catch(()=>{});
    }
  } catch (err) {
    console.warn("OST search failed, fallback to BGM:", err);
    if (bgm.paused) bgm.play().catch(()=>{});
  }
}


  function handleGamepad(pad) {
    const now = performance.now();
    const cooldown = 220; // ms between inputs
    if (now - lastInputTime < cooldown) return;

    const buttons = pad.buttons.map(b => b.pressed);
    const axes = pad.axes.map(a => Math.round(a * 10) / 10);

    // Left / Right navigation
    if (buttons[14] || axes[0] < -0.5) { // D-pad left or analog left
      goLeft();
      lastInputTime = now;
    } else if (buttons[15] || axes[0] > 0.5) { // D-pad right or analog right
      goRight();
      lastInputTime = now;
    }

    // A / Start to launch
    if (buttons[0] || buttons[9]) {
      launchGame();
      lastInputTime = now;
    }

    // B / Back to exit (placeholder)
    if (buttons[1] || buttons[8]) {
      console.log("Exit requested — close app manually or implement quit handler");
      lastInputTime = now;
    }
  }

  window.addEventListener("gamepadconnected", e => {
    console.log(`Gamepad connected: ${e.gamepad.id}`);
    activePad = e.gamepad;
  });

  window.addEventListener("gamepaddisconnected", e => {
    console.log("Gamepad disconnected");
    activePad = null;
  });

  pollGamepads();
  

  // === HIDDEN YOUTUBE IFRAME ===
  const iframe = document.createElement('div');
  iframe.id = 'yt-ost';
  iframe.style.display = 'none';
  document.body.appendChild(iframe);
});
