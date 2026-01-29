document.addEventListener("DOMContentLoaded", function () {

  const videos = document.querySelectorAll(".reel-video");


  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      const video = entry.target;

      if (entry.isIntersecting) {
        videos.forEach(v => {
          if (v !== video) {
            v.pause();
            v.currentTime = 0;
            v.muted = true;
          }
        });
        video.play().catch(() => {});
      } else {
        video.pause();
      }
    });
  }, { threshold: 0.6 });

  videos.forEach(video => {

    observer.observe(video);


    video.addEventListener("click", () => {
      video.muted = false;
      video.play();
      const text = video.nextElementSibling;
      if (text && text.classList.contains("tap-text")) {
        text.style.display = "none";
      }
    });

  });

  // SHARE BUTTON
  document.querySelectorAll(".share-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const url = btn.getAttribute("data-url");

      if (navigator.share) {
        await navigator.share({
          title: "Check this post",
          url: url
        });
      } else {
        navigator.clipboard.writeText(url);
        alert("Link copied!");
      }
    });
  });

});

