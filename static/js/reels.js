const videos=document.querySelectorAll("video");
const observer=new IntersectionObserver(entries=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      e.target.play();
    }else{
      e.target.pause();
      e.target.muted=true;
    }
  });
},{threshold:0.7});
videos.forEach(v=>observer.observe(v));


function enableSound(video){


  document.querySelectorAll("video").forEach(v=>{
    v.muted=true;
  });


  video.muted=false;
  video.volume=1;

  
  video.play().catch(()=>{});
}

function openComments(id){
  document.getElementById("commentBox-"+id).classList.add("active");
}
function closeComments(id){
  document.getElementById("commentBox-"+id).classList.remove("active");
}
function sendComment(id){
  const t=document.getElementById("commentText-"+id);
  if(!t.value.trim())return;

  fetch("/add-comment/",{
    method:"POST",
    headers:{
      "Content-Type":"application/x-www-form-urlencoded",
      "X-CSRFToken":document.querySelector('meta[name="csrf-token"]').content
    },
    body:`post_id=${id}&text=${t.value}`
  }).then(r=>r.json()).then(d=>{
    document.getElementById("commentList-"+id)
      .innerHTML+=`<p><b>@${d.user}</b> ${d.text}</p>`;
    document.getElementById("commentCount-"+id).innerText++;
    t.value="";
  });
}


function shareReel(id){
  const url=location.origin+"/reels/?reel="+id;
  navigator.share ? navigator.share({url}) : navigator.clipboard.writeText(url);
}
function downloadReel(videoUrl){
  const a = document.createElement("a");
  a.href = videoUrl;
  a.download = "reel.mp4";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}