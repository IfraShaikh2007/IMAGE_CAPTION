const imageInput = document.getElementById('imageInput');
const generateBtn = document.getElementById('generateBtn');
const memePreview = document.getElementById('memePreview');
const downloadBtn = document.getElementById('downloadBtn');
const taglineEl = document.getElementById('tagline');

let selectedImageFile = null;
let generatedMemeUrl = null;

const taglines = [
  "One click = instant viral vibes 🚀",
  "Memes > Therapy 😂",
  "Spice up the group chat 🔥",
  "Low effort. High LOLs 💯",
  "Fresh memes served daily 🍕"
];

function changeTagline() {
  if (taglineEl) {
    taglineEl.innerText = taglines[Math.floor(Math.random() * taglines.length)];
  }
}
if (taglineEl) {
  changeTagline();
  setInterval(changeTagline, 3000);
}

const loadingMessages = [
  "Cooking fresh memes 🍳",
  "Injecting sarcasm 😏",
  "Spicing up the internet 🌶",
  "Packing LOLs for you 📦",
  "Brewing dankness ☕"
];

imageInput.addEventListener('change', (e) => {
  selectedImageFile = e.target.files[0];
  memePreview.textContent = 'Image selected. Click "Generate Meme".';
  downloadBtn.disabled = true;
});

// Generate meme image via Flask backend with text overlay
generateBtn.addEventListener('click', async () => {
  if (!selectedImageFile) {
    alert('Please upload an image first.');
    return;
  }

  let i = 0;
  memePreview.textContent = loadingMessages[i];
  const loadingInterval = setInterval(() => {
    i = (i + 1) % loadingMessages.length;
    memePreview.textContent = loadingMessages[i];
  }, 1500);

  downloadBtn.disabled = true;
  const formData = new FormData();
  formData.append('image', selectedImageFile);

  try {
    const response = await fetch('/generate-meme', {
      method: 'POST',
      body: formData
    });
    if (!response.ok) throw new Error('Server returned ' + response.status);
    const blob = await response.blob();
    clearInterval(loadingInterval);
    generatedMemeUrl = URL.createObjectURL(blob);
    displayMeme(generatedMemeUrl);
    downloadBtn.disabled = false;
  } catch (error) {
    clearInterval(loadingInterval);
    memePreview.textContent = 'Error generating meme: ' + error.message;
    downloadBtn.disabled = true;
  }
});

// Download meme image
downloadBtn.addEventListener('click', () => {
  if (!generatedMemeUrl) return;
  const a = document.createElement('a');
  a.href = generatedMemeUrl;
  a.download = 'generated_meme.png';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
});

function displayMeme(url) {
  memePreview.innerHTML = '';
  const img = document.createElement('img');
  img.src = url;
  img.alt = 'Generated Meme';
  img.style.maxWidth = '100%';
  img.style.maxHeight = '100%';
  img.style.objectFit = 'contain';
  memePreview.appendChild(img);
}

// Navigation buttons
document.getElementById('navHome').addEventListener('click', () => {
  window.location.href = 'meme.html';
});
document.getElementById('navShortStory').addEventListener('click', () => {
  window.location.href = 'story.html';
});
document.getElementById('navCaptions').addEventListener('click', () => {
  window.location.href = 'caption.html';
});
